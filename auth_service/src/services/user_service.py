from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, List
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from fastapi import Request
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from starlette.responses import JSONResponse
from werkzeug.security import check_password_hash, generate_password_hash

from src.core.config import config
from src.db.pagination import PaginationParams
from src.models.entity import User, UserLoginHistory, Role, UserSocialAccount
from src.schemas.entity import (
    UserRegister,
    TokenResponse,
    RefreshTokenRequest,
    UpdateUserCredentialsRequest,
    UserLoginHistoryResponse,
    SocialUserRegister,
)
from src.services.async_pg_repository import PostgresAsyncRepository
from src.services.async_redis_repository import AsyncRedisRepository
from src.models.entity import PremiumData


class UserService:
    def __init__(
        self,
        db: PostgresAsyncRepository,
        redis: AsyncRedisRepository,
        secret_key: str,
        algorithm: str = "HS256",
    ):
        self.db = db
        self.redis = redis
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.access_token_exp_minutes = 15
        self.refresh_token_exp_days = 30

    async def check_blacklist(self, token: str) -> None:
        """
        Check if the token is in the blacklist and raise an exception if it is.
        """
        is_blacklisted = await self.redis.get(f"blacklist:{token}")
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked.",
            )

    async def get_user_id_from_token(self, token: str) -> str:
        """
        Extract the user ID from the given JWT access token.
        """
        # Check if the token is blacklisted
        await self.check_blacklist(token)

        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: subject not found.",
                )
            return user_id
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            )

    async def register_user(self, user_data: dict) -> User:
        """
        Register a new user by validating and creating the user in the database.
        :param user_data: Dictionary containing user registration data.
        :return: The created User ORM object.
        """
        # Check if the user already exists by login
        existing_user = await self.db.fetch_by_query_all(
            User, "login", user_data["login"]
        )
        existing_email = await self.db.fetch_by_query_all(
            User, "email", user_data["email"]
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this login already exists.",
            )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists.",
            )

        # Use the create_user method to handle the actual creation logic
        user_orm = await self.create_user(user_data)
        return user_orm

    async def create_user(self, user_data: dict) -> User:
        """
        Creates a new user in the database.
        This function handles validation, password hashing, and insertion of the user.
        :param user_data: Dictionary containing user data.
        :return: The created User ORM object.
        """
        try:
            # Validate the input data using the UserRegister Pydantic model
            if "password" in user_data:
                hashed_password = generate_password_hash(user_data["password"])
                user_data["password"] = hashed_password

            # Create a Pydantic model instance to validate the input data
            user = UserRegister(**user_data)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="All the required fields must be filled in.",
            )

        # Convert the Pydantic model to the ORM model
        user_orm = User(**user.dict())

        # Insert the new user into the database
        await self.db.insert(user_orm)
        return user_orm

    async def create_social_user(
        self, user_data: dict, provider: str, provider_user_id: str
    ) -> User:
        """
        Creates a new user in the database using a social account and links the social account.
        :param user_data: Dictionary containing user data from social providers.
        :param provider: The name of the social provider (e.g., 'google', 'vk').
        :param provider_user_id: The unique user ID from the social provider.
        :return: The created User ORM object.
        """
        try:
            # Use email as login or generate a dummy login if email is not available
            user_data["login"] = user_data.get(
                "email", f"{provider}_{uuid4()}")

            # Create a Pydantic model instance to validate the input data
            user = SocialUserRegister(**user_data)  # Validate the user data

        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="All the required fields must be filled in.",
            )

        # Remove any fields that are not part of the User model, such as 'name'
        user_data_dict = user.dict(exclude_unset=True)
        user_data_dict.pop("name", None)  # Remove 'name' field if it exists

        # Convert the Pydantic model to the ORM model, explicitly passing 'login'
        user_orm = User(**user_data_dict, login=user_data.get("login"))

        # Insert the new user into the database
        await self.db.insert(user_orm)

        # After user creation, link the social account
        user_social_account = UserSocialAccount(
            user_id=user_orm.id,
            provider=provider,
            provider_user_id=provider_user_id,
            fullname=user.name,
        )

        # Insert the new social account record
        await self.db.insert(user_social_account)

        return user_orm

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_exp_minutes
            )
        to_encode.update({"exp": expire})

        # Convert UUIDs to strings
        to_encode = {
            k: (str(v) if isinstance(v, UUID) else v) for k, v in to_encode.items()
        }

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: UUID) -> str:
        to_encode = {"sub": str(user_id)}
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_exp_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def record_login(
        self,
        user_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserLoginHistory:
        """
        Record the login event for the given user, including user agent and IP address.
        """
        # Create a login history instance
        login_history = UserLoginHistory(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            login_time=datetime.utcnow(),
        )

        # Save the login history record to the database
        await self.db.insert(login_history)

        return login_history

    async def check_premium_status(self, user_id: UUID) -> bool:
        """
        Method for check is user has premium status.
        :param user_id:
        :return:
        """
        premium = await self.db.fetch_by_query_first(
            PremiumData, "user_id", user_id
        )
        if not premium or premium.valid_until < datetime.now():
            return False
        return True

    async def login(self, login_data: dict, request: Request) -> TokenResponse:
        # Fetch the user from the database by login
        user: User = await self.db.fetch_by_query_first(
            User, "login", login_data["login"]
        )

        # If the user doesn't exist or the password is incorrect, raise an error
        if not user or not check_password_hash(user.password, login_data["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password.",
            )

        # Generate access and refresh tokens
        access_token = self.create_access_token(
            data={
                "sub": user.id,
                "login": user.login,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": user.is_superuser,
                "is_active": user.is_active,
                "is_premium": await self.check_premium_status(user.id),
            }
        )
        refresh_token = self.create_refresh_token(user.id)

        # Save refresh token in Redis
        await self.redis.set(
            f"refresh_token:{user.id}",
            refresh_token,
            expire=self.refresh_token_exp_days * 24 * 60 * 60,
        )

        # Extract user agent and IP address from the request
        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = request.client.host

        # Record the login event
        await self.record_login(user.id, user_agent=user_agent, ip_address=ip_address)

        # Return the token response
        return TokenResponse(
            access_token=access_token, token_type="bearer", refresh_token=refresh_token
        )

    async def refresh_access_token(self, refresh_request: dict) -> TokenResponse:
        try:
            # Validate the refresh request using the Pydantic model
            refresh_token_model = RefreshTokenRequest(**refresh_request)
            refresh_token = refresh_token_model.refresh_token

            # Decode the refresh token
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )
            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify that the refresh token exists in Redis
            stored_token = await self.redis.get(f"refresh_token:{user_id}")
            if stored_token is None or stored_token != refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Generate a new access token
            access_token = self.create_access_token(data={"sub": user_id})

            # Regenerate a new refresh token
            new_refresh_token = self.create_refresh_token(user_id)
            await self.redis.set(
                f"refresh_token:{user_id}",
                new_refresh_token,
                expire=self.refresh_token_exp_days * 60 * 60 * 24,
            )

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                refresh_token=new_refresh_token,
            )

        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def logout(self, user_id: str, access_token: str, refresh_token: str) -> None:
        try:
            # Remove the refresh token from Redis
            stored_refresh_token = await self.redis.get(f"refresh_token:{user_id}")
            if (
                stored_refresh_token is not None
                and stored_refresh_token == refresh_token
            ):
                await self.redis.delete(f"refresh_token:{user_id}")

            # Add the access token to the blacklist
            access_token_ttl = self._get_token_ttl(
                access_token
            )  # Calculate the TTL from the token
            if access_token_ttl > 0:
                await self.redis.set(
                    f"blacklist:{access_token}", "blacklisted", expire=access_token_ttl
                )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during logout.",
            )

    def _get_token_ttl(self, token: str) -> int:
        """
        Calculate the TTL (time-to-live) for the access token based on its expiration time.
        """
        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            expiration_time = datetime.fromtimestamp(payload["exp"])
            current_time = datetime.utcnow()
            ttl = (expiration_time - current_time).total_seconds()
            return max(0, int(ttl))  # Ensure TTL is non-negative
        except ExpiredSignatureError:
            # If the token has expired, return 0 to indicate no TTL
            return 0
        except JWTError:
            # Handle other JWT errors if necessary
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def update_user_credentials(
        self, user_id: str, update_request: UpdateUserCredentialsRequest
    ) -> User:
        """
        Update the user's credentials, handling both login and password changes.
        """
        # Fetch the user by ID
        user = await self.db.fetch_by_query_first(User, "id", user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        # Extract update data
        update_data = update_request.dict(exclude_unset=True)

        # Update the login, first_name and last_name if provided
        if "login" in update_data:
            user.login = update_data["login"]
        if "first_name" in update_data:
            user.first_name = update_data["first_name"]
        if "last_name" in update_data:
            user.last_name = update_data["last_name"]

        # Update the password if both old and new passwords are provided
        if "old_password" in update_data and "new_password" in update_data:
            if not check_password_hash(user.password, update_data["old_password"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Old password is incorrect.",
                )
            user.password = generate_password_hash(update_data["new_password"])

        try:
            # Save changes to the database
            await self.db.update(user)

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The login is already taken.",
            )

        return user

    async def get_login_history(self, user_id: str) -> List[UserLoginHistoryResponse]:
        """
        Retrieve the login history for the specified user.
        """
        # Fetch the login history for the user from the database
        login_history = await self.db.fetch_by_query_all(
            UserLoginHistory, "user_id", user_id
        )

        if not login_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No login history found for this user.",
            )

        # Convert the ORM instances to Pydantic models
        return [UserLoginHistoryResponse.from_orm(entry) for entry in login_history]

    async def get_login_history_paginated(
        self, user_id: str, pagination: PaginationParams
    ) -> tuple[list[UserLoginHistory], int]:
        """
        Retrieve the login history for the specified user with pagination.
        """
        async with self.db.async_session() as session:  # Create a session from sessionmaker
            stmt = (
                select(UserLoginHistory)
                .where(UserLoginHistory.user_id == user_id)
                .limit(pagination.page_size)
                .offset((pagination.page - 1) * pagination.page_size)
            )

            # Execute the query
            result = await session.execute(stmt)
            login_history = result.scalars().all()

            # Calculate total count
            total_count_stmt = select(func.count(UserLoginHistory.id)).where(
                UserLoginHistory.user_id == user_id
            )
            total_count_result = await session.execute(total_count_stmt)
            total_count = total_count_result.scalar()

            return login_history, total_count

    async def is_superuser(self, user_id: str) -> bool:
        user = await self.db.fetch_by_id(User, user_id)
        return user.is_superuser

    async def is_anonymous(self, user_id: str) -> bool:
        user = await self.db.fetch_by_id(User, user_id)
        return user.is_anonymous

    async def get_user_permissions(self, user_id: str) -> list[str]:
        if await self.is_superuser(user_id):
            return ["*"]  # Superusers have all permissions

        user = await self.db.fetch_by_id(User, user_id)
        if await self.is_anonymous(user_id):
            return ["read"]  # Default permissions for anonymous users

        permissions = set()
        for role in user.roles:
            role = await self.db.fetch_by_id(Role, role.role_id)
            role_permissions = role.permissions
            permissions.update(role_permissions)

        return list(permissions)

    async def authorize(self, user_id: str, permission: str) -> bool:
        # First, check if the user is a superuser
        if await self.is_superuser(user_id):
            return True

        # Get user permissions
        user_permissions = await self.get_user_permissions(user_id)
        return permission in user_permissions

    async def get_or_create_user_from_oauth(self, provider: str, user_info: dict):
        """
        Retrieves the user by their OAuth provider's user ID or creates a new one if not found.

        :param provider: The OAuth provider name (e.g., 'google', 'facebook').
        :param user_info: The user's information provided by the OAuth provider.
        :return: The User ORM object.
        """
        # Extract provider-specific user ID (e.g., 'sub' for Google)
        provider_user_id = user_info.get("sub")
        if not provider_user_id:
            raise ValueError(
                f"User info from {provider} is missing the 'sub' field.")

        # Check if the user already exists by provider user ID
        user = await self.get_user_by_provider_id(provider, provider_user_id)
        if user:
            return user

        # If the user doesn't exist, create a new social user
        new_user_data = {
            "email": user_info.get("email"),
            "first_name": user_info.get("given_name"),
            "last_name": user_info.get("family_name"),
            "is_active": True,
        }
        new_user = await self.create_social_user(
            new_user_data, provider=provider, provider_user_id=provider_user_id
        )

        return new_user

    async def get_user_by_provider_id(
        self, provider: str, provider_user_id: str
    ) -> User | None:
        """
        Fetch the user from the database by their OAuth provider's user ID and provider name.

        :param provider: The OAuth provider name (e.g., 'google', 'facebook').
        :param provider_user_id: The unique user ID from the OAuth provider.
        :return: The User object if found, otherwise None.
        """
        # Use fetch_by_query_first_many_conditions to query by both provider and provider_user_id
        user_social_account = await self.db.fetch_by_query_first_many_conditions(
            model_class=UserSocialAccount,
            columns_values=[
                ("provider", provider),
                ("provider_user_id", provider_user_id),
            ],
        )

        if user_social_account is None:
            return None

        # Fetch the associated user from the social account
        user = await self.db.fetch_by_id(User, user_social_account.user_id)
        return user

    async def get_user_info(self, user_id: UUID) -> TokenResponse:
        # Fetch the user from the database by ID.
        user: User = await self.db.fetch_by_query_first(User, "id", user_id)

        # If the user doesn't exist - raise an error
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect user's ID."
            )

        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser,
        }

    async def set_premium(
        self, user_id: str, number_of_month: int
    ) -> bool:
        """
        Set user's status - premium.
        """

        # Fetch the user by ID
        user = await self.db.fetch_by_query_first(User, "id", user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        # Check premium user
        check_premium = await self.db.fetch_by_query_first(PremiumData, "user_id", user_id)

        if check_premium is True:
            return False

        premium = PremiumData(user_id=user_id, valid_until=datetime.now(
        )+relativedelta(months=number_of_month))
        # Set up a premium account for the user
        try:
            await self.db.insert(premium)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error of changing user's status.",
            )

        return True


def get_user_service() -> UserService:
    return UserService(
        db=PostgresAsyncRepository(dsn=config.dsn),
        redis=AsyncRedisRepository(redis_url=config.redis_url),
        secret_key=config.secret_key,
        algorithm="HS256",
    )

from uuid import UUID

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from src.core.config import config
from src.models.entity import Role, User, UserRole
from src.schemas.entity import (
    RoleCreate,
    RoleInDB,
    RolesInDB,
    RoleId,
    UpdateRoleRequest,
    UserPermissions,
)
from src.services.async_pg_repository import PostgresAsyncRepository
from src.services.user_service import get_user_service


class RoleService:
    def __init__(self, db: PostgresAsyncRepository):
        self.db = db

    async def create_role(self, role_data: dict) -> Role:
        """
        Create new role.
        @param role_data: Name, description, permissions of role.
        @return: Created role.
        """

        # Check if the role already exists by role's name
        existing_role = await self.db.fetch_by_query_all(
            Role, "name", role_data["name"]
        )

        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists."
            )

        try:
            # Validate role_data
            role = RoleCreate(**role_data)

        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="All the required fields must be filled in.",
            )
        role_orm = Role(**role.model_dump(mode="json"))
        await self.db.insert(role_orm)
        return role_orm

    async def get_roles(self) -> RolesInDB:
        """
        Return all roles.
        """

        # Get all roles.
        roles = await self.db.fetch_all(Role)

        if not roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="There is no roles."
            )

        roles_model = RolesInDB(
            roles=[RoleInDB(**role.to_dict()) for role in roles])

        return roles_model

    async def delete_role(self, role_id: UUID):
        """
        Delete the role by ID.
        @param role_id: ID of the role.
        @return:
        """
        try:
            # Validate role UUID
            validated_role_id = RoleId(id=role_id)

        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Enter correct UUID.",
            )

        # Check if the role exists
        existing_role = await self.db.fetch_by_query_all(
            Role, "id", validated_role_id.id
        )

        if not existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role doesn't exist."
            )

        await self.db.delete(Role, validated_role_id.id)

    async def update_role(self, role_id: UUID, role_data: UpdateRoleRequest) -> Role:
        """
        Update role data.
        @param role_id: ID of the role.
        @param role_data:  Name, description, permissions of the role.
        @return: Updated role.
        """
        # Fetch the role by ID
        role = await self.db.fetch_by_query_first(Role, "id", role_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role doesn't exist."
            )
        update_data = role_data.dict(exclude_unset=True)

        if "name" in update_data:
            role.name = update_data["name"]
        if "description" in update_data:
            role.description = update_data["description"]
        if "permissions" in update_data:
            role.permissions = update_data["permissions"]

        try:
            await self.db.update(role)

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The name of the role is already taken.",
            )

        return role

    async def assign_role_to_user(self, user_id: UUID, role_name: str) -> None:
        """
        Assign role to the user
        @param user_id: ID of the user.
        @param role_name: Name of the role.
        """
        # Fetch the role by ID
        role = await self.db.fetch_by_query_first(Role, "name", role_name)

        # Fetch the user by ID
        user = await self.db.fetch_by_query_first(User, "id", user_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role doesn't exist."
            )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist."
            )

        existing_user_role = await self.db.fetch_by_query_first_many_conditions(
            UserRole, [("user_id", user.id), ("role_id", role.id)]
        )
        if existing_user_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this role.",
            )

        user_role = UserRole(user_id=user.id, role_id=role.id)

        await self.db.insert(user_role)

    async def remove_role_from_user(self, user_id: UUID, role_name: str) -> None:
        """
        Remove role from the user
        @param user_id: ID of the user.
        @param role_name: Name of the role.
        """
        # Fetch the role by ID
        role = await self.db.fetch_by_query_first(Role, "name", role_name)

        # Fetch the user by ID
        user = await self.db.fetch_by_query_first(User, "id", user_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role doesn't exist."
            )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist."
            )

        existing_user_role = await self.db.fetch_by_query_first_many_conditions(
            UserRole, [("user_id", user.id), ("role_id", role.id)]
        )
        if not existing_user_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User doesn't have this role.",
            )

        await self.db.delete(UserRole, existing_user_role.id)

    async def check_user_permissions(self, user_id: UUID) -> UserPermissions:
        """
        Get permissions of the user from all user's roles by user ID.
        @param user_id: ID of User
        """
        # Fetch the user by ID
        user = await self.db.fetch_by_query_first(User, "id", user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist."
            )

        # Get all user's roles with Role joined filed
        user_roles = await self.db.fetch_by_query_all_joinedload(
            UserRole, "user_id", user_id, "role"
        )

        if not user_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User hasn't permissions.",
            )

        # Get permissions from all user's roles
        user_permissions = []
        for user_role in user_roles:
            role_permissions = user_role.role.permissions
            user_permissions.extend(role_permissions)

        return UserPermissions(permissions=user_permissions)

    async def check_is_superuser_by_access_token(
        self,
        access_token: str = Depends(
            OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
        ),
    ):
        """
        Check is user a superuser by access token.
        @param access_token: User's access token.
        """

        # Use user_service functions for working with token.
        user_service = get_user_service()

        # Extract the user ID from the access token
        user_id = await user_service.get_user_id_from_token(access_token)
        is_superuser = await user_service.is_superuser(user_id)

        return is_superuser


def get_role_service() -> RoleService:
    return RoleService(db=PostgresAsyncRepository(dsn=config.dsn))

import logging
from uuid import UUID

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Body, status, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer


from src.core.config import config
from src.db.pagination import PaginationParams, PaginatedResponse
from src.models.entity import User
from src.schemas.entity import (
    UserRegister,
    UserInDB,
    UserLogin,
    TokenResponse,
    LogoutRequest,
    GetUserInfoRequest,
    UpdateUserCredentialsRequest,
    UserResponse,
    UserLoginHistoryResponse,
)
from src.services.user_service import UserService, get_user_service

from src.schemas.entity import UserInfoOut

from src.schemas.entity import GetAccessToken

from src.schemas.entity import SetUserPremiumRequest

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth client using settings from the `config`
oauth.register(
    name="google",
    client_id=config.google_client_id,
    client_secret=config.google_client_secret,
    server_metadata_url=config.google_metadata_url,
    client_kwargs={"scope": "openid email profile"},
)


@router.post(
    "/register",
    response_model=UserInDB,
    summary="Register a new user",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserRegister = Body(..., description="User registration data"),
    user_service: UserService = Depends(get_user_service),
) -> UserInDB:
    logging.info("register_user")
    # Register the user and get the created user's data
    user = await user_service.register_user(user_data.dict())

    # Convert the saved user data to the response model
    return UserInDB(**user.to_dict())


@router.post("/login", response_model=TokenResponse, summary="Login a user")
async def login_user(
    login_data: UserLogin = Body(..., description="User login data"),
    user_service: UserService = Depends(get_user_service),
    request: Request = None,  # Add the Request object here
) -> TokenResponse:
    # Authenticate the user and get the tokens
    token_response = await user_service.login(login_data.dict(), request)

    # Return the token response
    return token_response


@router.post(
    "/refresh", response_model=TokenResponse, summary="Refresh a token for user"
)
async def refresh_user_token(
    refresh_request: dict = Body(..., description="User's refresh token"),
    user_service: UserService = Depends(get_user_service),
) -> TokenResponse:
    # Refresh the access token using the provided refresh token
    token_response = await user_service.refresh_access_token(refresh_request)

    # Return the token response
    return token_response


@router.post(
    "/logout",
    summary="Logout a user and invalidate their tokens",
    status_code=status.HTTP_200_OK,
)
async def logout_user(
    logout_request: LogoutRequest = Body(...,
                                         description="User's refresh token"),
    access_token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    """
    Invalidate the access and refresh tokens for the user.
    """

    # Extract the user ID from the access token
    user_id = user_service.get_user_id_from_token(access_token)

    # Perform the logout operation
    await user_service.logout(user_id, access_token, logout_request.refresh_token)

    # Return a success response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "User successfully logged out."},
    )


@router.patch(
    "/update",
    summary="Partially update user login or password",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def update_user_credentials(
    update_request: UpdateUserCredentialsRequest = Body(
        ..., description="User credentials update data"
    ),
    user_service: UserService = Depends(get_user_service),
    access_token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
) -> User:
    """
    Update the user's login or password.
    """
    try:
        # Extract the user ID from the access token
        user_id = await user_service.get_user_id_from_token(access_token)

        # Delegate the update logic to the service method
        updated_user = await user_service.update_user_credentials(
            user_id, update_request
        )

        return updated_user

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user credentials.",
        )


@router.get(
    "/login-history", response_model=PaginatedResponse[UserLoginHistoryResponse]
)
async def get_user_login_history(
    user_service: UserService = Depends(get_user_service),
    access_token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[UserLoginHistoryResponse]:
    """
    Retrieve the login history for the authenticated user.
    """
    try:
        # Extract the user ID from the access token
        user_id = await user_service.get_user_id_from_token(access_token)

        # Get the login history
        login_history, total_count = await user_service.get_login_history_paginated(
            user_id, pagination
        )

        total_pages = (total_count + pagination.page_size -
                       1) // pagination.page_size

        return PaginatedResponse(
            count=len(login_history),
            total_pages=total_pages,
            prev=pagination.page - 1 if pagination.page > 1 else None,
            next=pagination.page + 1 if pagination.page < total_pages else None,
            results=login_history,
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the login history.",
        )


@router.get("/{provider}/login", summary="Initiate OAuth login")
async def login_via_oauth(provider: str, request: Request):
    # Dynamically get the correct OAuth provider based on the URL parameter
    oauth_provider = getattr(oauth, provider, None)
    if not oauth_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider.",
        )

    # Dynamically create the redirect URI for the callback
    redirect_uri = request.url_for("auth_callback", provider=provider)

    # Initiate the OAuth authorization process for the selected provider
    return await oauth_provider.authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def auth_callback(
    provider: str,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    # Dynamically get the correct OAuth provider based on the URL parameter
    oauth_provider = getattr(oauth, provider, None)
    if not oauth_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider.",
        )

    # Authorize the access token from the selected provider
    token = await oauth_provider.authorize_access_token(request)
    userinfo = token.get("userinfo")

    # Extract the id_token (if available) and other relevant information
    id_token = token.get("id_token", None)
    if not userinfo or not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve necessary information from provider.",
        )

    # Extract user information from the token
    provider_user_id = userinfo.get("sub")
    email = userinfo.get("email")

    # Ensure mandatory fields are available
    if not provider_user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing necessary user information from provider.",
        )

    # Get or create the user in your system based on provider account details
    user = await user_service.get_or_create_user_from_oauth(provider, userinfo)

    # Generate an access token for the user
    token_response = user_service.create_access_token({"sub": user.id})

    # Return the access token to the client
    return JSONResponse(
        content={"access_token": token_response, "token_type": "bearer"}
    )


@router.post(
    "/get-user-info",
    summary="Get user's email, first name, last name by ID.",
    status_code=status.HTTP_200_OK,
)
async def get_user_info(
    user: GetUserInfoRequest = Body(..., description="User's ID."),
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    """
    Invalidate the access and refresh tokens for the user.
    """

    # Extract the user ID from the access token
    user_info = await user_service.get_user_info(user_id=user.user_id)
    # Convert UUIDs to strings to ensure JSON serialization compatibility
    user_info_serializable = {
        key: str(value) if isinstance(value, UUID) else value
        for key, value in user_info.items()
    }

    # Return a success response
    return JSONResponse(status_code=status.HTTP_200_OK, content=user_info_serializable)


@router.post(
    "/user-info",
    response_model=UserInfoOut,
    summary="Get user's info by access token.",
    status_code=status.HTTP_200_OK,
)
async def get_user_info_by_token(
    user_service: UserService = Depends(get_user_service),
    token: GetAccessToken = Body(..., description="User's access token"),
):
    """
    Retrieve the user's info by access token.
    """
    try:
        # Extract the user's ID from the access token
        user_id = await user_service.get_user_id_from_token(token.access_token)

        # Extract the user's info by user_id
        user_info = await user_service.get_user_info(user_id=user_id)

        return UserInfoOut(**user_info)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the user's info.",
        )

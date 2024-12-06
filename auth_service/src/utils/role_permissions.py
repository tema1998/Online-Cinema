from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.services.role_service import get_role_service, RoleService


async def only_for_superuser(
    access_token: str = Depends(
        OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")),
    role_service: RoleService = Depends(get_role_service),
) -> None:
    """
    Check whether the user is a superuser.
    @param access_token: Dependency for getting access token of the current user.
    @param role_service: Role service.
    """
    if not await role_service.check_is_superuser_by_access_token(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be a superuser to execute this action.",
        )

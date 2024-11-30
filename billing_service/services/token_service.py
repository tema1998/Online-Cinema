import http
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import config
from services.auth_service import get_auth_service


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        self.auth_service = get_auth_service()
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )
        user_info = await self.get_user_info_from_auth_service(credentials.credentials)
        return user_info

    async def get_user_info_from_auth_service(self, jwt_token: str) -> Optional[dict]:
        user_info = await self.auth_service.make_request_to_auth_service(jwt_token)
        return user_info


get_user_info = JWTBearer()

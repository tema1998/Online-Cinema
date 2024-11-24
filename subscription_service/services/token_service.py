import json

import aiohttp
import requests
import http
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import config

async def make_request_to_auth_service(access_token:str) -> dict:
    # Request parameters
    url = config.auth_service_get_user_info_url
    body = {"access_token": access_token}

    try:
        # Make async request to Auth-service
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=json.dumps(body), headers={"Content-Type": "application/json"}) as response:
                response_json = await response.json()
    except:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail='Error connecting to the authorization service')

    if response.status == 401:
        raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid authorization code.')
    if response.status != 200:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST,
                            detail='Error connecting to the authorization service')

    # Get user's data from json response
    return {'id': response_json.get('id'), 'email': response_json.get('email'),
            'first_name': response_json.get('first_name'), 'last_name': response_json.get('last_name'),}

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid authorization code.')
        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail='Only Bearer token might be accepted')
        user_info = await self.get_user_info_from_auth_service(credentials.credentials)
        return user_info

    @staticmethod
    async def get_user_info_from_auth_service(jwt_token: str) -> Optional[dict]:
        user_info = await make_request_to_auth_service(jwt_token)
        return user_info


get_user_info = JWTBearer()

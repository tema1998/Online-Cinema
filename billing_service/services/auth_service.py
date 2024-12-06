import json
import uuid

import aiohttp
import http
from typing import Optional
from fastapi import HTTPException

from core.config import config


class AuthService:
    def __init__(self):
        self.auth_service_url = config.auth_service_url
        self.auth_service_get_user_info = config.auth_service_get_user_info
        self.auth_service_set_premium_user = config.auth_service_set_premium_user

    async def make_request_to_set_premium(self, user_id: uuid, number_of_month: int):
        # Request parameters
        body = {"user_id": str(user_id),
                "number_of_month": number_of_month}

        try:

            # Make async request to Auth-service
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=self.auth_service_url + self.auth_service_set_premium_user,
                    data=json.dumps(body),
                    headers={"Content-Type": "application/json"},
                ) as response:
                    response_json = await response.json()

        except:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Error connecting to the authorization service",
            )

    async def make_request_to_auth_service(self, access_token: str) -> dict:
        # Request parameters
        body = {"access_token": access_token}

        try:
            # Make async request to Auth-service
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=self.auth_service_url + self.auth_service_get_user_info,
                        data=json.dumps(body),
                        headers={"Content-Type": "application/json"},
                ) as response:
                    response_json = await response.json()
        except:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Error connecting to the authorization service",
            )

        if response.status == 401:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid authorization code."
            )
        if response.status != 200:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Error connecting to the authorization service",
            )

        # Get user's data from json response
        return {
            "id": response_json.get("id"),
            "email": response_json.get("email"),
            "first_name": response_json.get("first_name"),
            "last_name": response_json.get("last_name"),
        }


def get_auth_service():
    return AuthService()

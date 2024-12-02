import json
from http import HTTPStatus
from uuid import UUID
from aiohttp import ClientSession
from fastapi import HTTPException
from billing_worker.config.settings import settings


class SetPremiumSubscriptionService:
    def __init__(self, auth_service_url: str, auth_service_set_premium_user: str, billing_service_url: str, billing_service_change_order_status: str):
        self.auth_service_url = auth_service_url
        self.auth_service_set_premium_user = auth_service_set_premium_user
        self.billing_service_url = billing_service_url
        self.billing_service_change_order_status = billing_service_change_order_status

    async def make_request_to_set_premium(self, user_id: UUID, number_of_month: int):
        # Request parameters
        body = {
            "user_id": str(user_id),
            "number_of_month": number_of_month
        }

        try:
            # Make async request to Auth-service
            async with ClientSession() as session:
                async with session.post(
                    url=self.auth_service_url + self.auth_service_set_premium_user,
                    data=json.dumps(body),
                    headers={"Content-Type": "application/json"},
                ) as response:
                    response_json = await response.json()
                    return response_json

        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Error connecting to the authorization service: {e}",
            )

    async def make_request_to_change_order_status(self, order_id: UUID, order_status: str):
        # Request parameters
        body = {
            "order_id": str(order_id),
            "order_status": order_status
        }

        try:
            # Make async request to Billing-service
            async with ClientSession() as session:
                async with session.post(
                    url=self.billing_service_url + self.billing_service_change_order_status,
                    data=json.dumps(body),
                    headers={"Content-Type": "application/json"},
                ) as response:
                    response_json = await response.json()
                    return response_json

        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Error connecting to the billing service: {e}",
            )

async def get_premium_service_setter():
    return SetPremiumSubscriptionService(
        settings.auth_service_url,
        settings.auth_service_set_premium_user,
        settings.billing_service_url,
        settings.billing_service_change_order_status
    )
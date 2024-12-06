import json
from http import HTTPStatus
from uuid import UUID

from aiohttp import ClientSession
from fastapi import HTTPException

from billing_worker.config.settings import settings


class SetFilmToUserService:
    def __init__(self, billing_service_url: str,
                 billing_service_change_order_status: str, notification_service_url_success: str,
                 notification_service_url_fail: str):
        self.billing_service_url = billing_service_url
        self.billing_service_change_order_status = billing_service_change_order_status
        self.notification_service_url_success = notification_service_url_success
        self.notification_service_url_fail = notification_service_url_fail

    async def make_request_to_change_order_status(self, order_type: str, order_id: UUID, order_status: str):
        # Request parameters
        body = {
            "order_type": order_type,
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

    async def make_request_to_notify_on_successful_payment(self, message_data: dict):

        try:
            # Make async request to Notification-service
            async with ClientSession() as session:
                async with session.post(
                        url=self.notification_service_url_success,
                        data=json.dumps(message_data),
                        headers={"Content-Type": "application/json"},
                ) as response:
                    response_json = await response.json()
                    return response_json

        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Error connecting to the notification service: {e}",
            )

    async def make_request_to_notify_on_failed_payment(self, message_data: dict):
        try:
            # Make async request to Notification-service
            async with ClientSession() as session:
                async with session.post(
                        url=self.notification_service_url_fail,
                        data=json.dumps(message_data),
                        headers={"Content-Type": "application/json"},
                ) as response:
                    response_json = await response.json()
                    return response_json

        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Error connecting to the notification service: {e}",
            )


async def get_film_service_setter():
    return SetFilmToUserService(
        settings.billing_service_url,
        settings.billing_service_change_order_status,
        settings.notification_successful_payment,
        settings.notification_failed_payment
    )

import json
from functools import lru_cache

import orjson
from fastapi import Depends

from notification_service.schemas.messages import (
    InstantMessageRequest,
)
from notification_service.services.broker_service import RabbitMQService


class MessageSendException(Exception):
    pass


class MessageService:
    def __init__(self, broker_service: RabbitMQService = Depends()):
        self.broker_service = broker_service

    async def send_single_message(
        self, content_id, message: InstantMessageRequest, message_transfer, queue_name
    ):
        try:
            message_body = json.dumps(
                {
                    "content_id": str(content_id),
                    "email": message.email,
                    "message_transfer": message_transfer,
                    "message_type": "instant",
                    "message_data": message.message_data,
                }
            )
            return await self.broker_service.publish(message_body, queue_name)

        except Exception as e:
            raise MessageSendException(
                "Failed to send message to broker: %s" % str(e))

    async def send_welcome_message(
        self, user_email, message: dict, message_transfer, queue_name
    ):
        try:
            message_body = json.dumps(
                {
                    "email": user_email,
                    "message_transfer": message_transfer,
                    "message_type": "welcome",
                    "message_data": message,
                }
            )
            return await self.broker_service.publish(message_body, queue_name)

        except Exception as e:
            raise MessageSendException(
                "Failed to send message to broker: %s" % str(e))

    async def send_notification_about_new_comment(
        self, review_id, email, message_data: dict, message_transfer, queue_name
    ):
        try:
            message_body = json.dumps(
                {
                    "review_id": str(review_id),
                    "email": email,
                    "message_transfer": message_transfer,
                    "message_type": "instant",
                    "message_data": message_data,
                }
            )
            return await self.broker_service.publish(message_body, queue_name)

        except Exception as e:
            raise MessageSendException(
                "Failed to send message to broker: %s" % str(e))

    async def send_notification_about_successful_payment(
        self, order_type: str, email: str, message_data: dict, message_transfer, queue_name
    ):
        if order_type == "premium":
            message_type = "successful_premium_payment"
        elif order_type == "film":
            message_type = "successful_film_payment"
        else:
            raise MessageSendException("Unknown type of order.")

        try:
            message_body = orjson.dumps(
                {
                    "email": email,
                    "message_transfer": message_transfer,
                    "message_type": message_type,
                    "message_data": message_data,
                }
            ).decode("utf-8")
            return await self.broker_service.publish(message_body, queue_name)

        except Exception as e:
            raise MessageSendException(
                "Failed to send message to broker: %s" % str(e))

    async def send_notification_about_failed_payment(
        self, order_type: str, email: str, message_data: dict, message_transfer, queue_name
    ):

        if order_type == "premium":
            message_type = "failed_premium_payment"
        elif order_type == "film":
            message_type = "failed_film_payment"
        else:
            raise MessageSendException("Unknown type of order.")

        try:
            message_body = orjson.dumps(
                {
                    "email": email,
                    "message_transfer": message_transfer,
                    "message_type": message_type,
                    "message_data": message_data,
                }
            ).decode("utf-8")
            return await self.broker_service.publish(message_body, queue_name)

        except Exception as e:
            raise MessageSendException(
                "Failed to send message to broker: %s" % str(e))


@lru_cache
def get_message_service(message_service: MessageService = Depends()):
    return message_service

import json
import logging

import aio_pika

from billing_worker.config.settings import settings
from billing_worker.consumers.base_consumer import BaseConsumer
from billing_worker.services.set_premium_status import get_premium_service_setter


class SubscriptionSuccessConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(
            queue_name=settings.billing_premium_subscription_success_queue,
            queue_name_dlq=settings.billing_premium_subscription_success_dlq,
        )

    async def handle_message(self, message: aio_pika.IncomingMessage):
        setter_premium_service = await get_premium_service_setter()
        async with message.process(ignore_processed=True):
            try:
                message_data = json.loads(message.body.decode())
                logging.info(f"Received message: {message_data}")

                number_of_months = message_data.get("number_of_month")
                user_id = message_data.get("user_id")
                order_id = message_data.get("order_id")
                await setter_premium_service.make_request_to_set_premium(user_id, number_of_months)
                await setter_premium_service.make_request_to_change_order_status(order_id, "Success")
                await setter_premium_service.make_request_to_notify_on_successful_payment(message_data)


            except Exception as e:
                await message.reject(requeue=False)
                logging.error(f"Error handling message: {str(e)}")


class SubscriptionFailConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(
            queue_name=settings.billing_premium_subscription_fail_queue,
            queue_name_dlq=settings.billing_premium_subscription_fail_dlq,
        )

    async def handle_message(self, message: aio_pika.IncomingMessage):
        setter_premium_service = await get_premium_service_setter()
        async with message.process(ignore_processed=True):
            try:
                message_data = json.loads(message.body.decode())
                logging.info(f"Received message: {message_data}")

                order_id = message_data.get("order_id")
                await setter_premium_service.make_request_to_change_order_status(order_id, "Fail")
                await setter_premium_service.make_request_to_notify_on_failed_payment(message_data)


            except Exception as e:
                await message.reject(requeue=False)
                logging.error(f"Error handling message: {str(e)}")

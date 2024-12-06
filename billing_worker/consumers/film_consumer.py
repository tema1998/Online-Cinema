import json
import logging

import aio_pika

from billing_worker.config.settings import settings
from billing_worker.consumers.base_consumer import BaseConsumer
from billing_worker.services.set_film_to_user import get_film_service_setter


class PurchaseFilmSuccessConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(
            queue_name=settings.billing_film_purchase_success_queue,
            queue_name_dlq=settings.billing_film_purchase_success_dlq,
        )

    async def handle_message(self, message: aio_pika.IncomingMessage):
        setter_premium_service = await get_film_service_setter()
        async with message.process(ignore_processed=True):
            try:
                message_data = json.loads(message.body.decode())
                logging.info(f"Received message: {message_data}")

                order_type = message_data.get("order_type")
                order_id = message_data.get("order_id")

                await setter_premium_service.make_request_to_change_order_status(order_type, order_id, "Success")
                await setter_premium_service.make_request_to_notify_on_successful_payment(message_data)

            except Exception as e:
                await message.reject(requeue=False)
                logging.error(f"Error handling message: {str(e)}")


class PurchaseFilmFailConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(
            queue_name=settings.billing_film_purchase_fail_queue,
            queue_name_dlq=settings.billing_film_purchase_fail_dlq,
        )

    async def handle_message(self, message: aio_pika.IncomingMessage):
        setter_premium_service = await get_film_service_setter()
        async with message.process(ignore_processed=True):
            try:
                message_data = json.loads(message.body.decode())
                logging.info(f"Received message: {message_data}")

                order_type = message_data.get("order_type")
                order_id = message_data.get("order_id")

                await setter_premium_service.make_request_to_change_order_status(order_type, order_id, "Fail")
                await setter_premium_service.make_request_to_notify_on_failed_payment(message_data)

            except Exception as e:
                await message.reject(requeue=False)
                logging.error(f"Error handling message: {str(e)}")

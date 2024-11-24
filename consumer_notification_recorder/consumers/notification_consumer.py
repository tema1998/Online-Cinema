import json
import logging

import aio_pika

from consumer_notification_recorder.config.settings import settings
from consumer_notification_recorder.consumers.base_consumer import BaseConsumer
from consumer_notification_recorder.services.notification_recorder_service import get_notification_service


class NotificationConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(queue_name=settings.instant_notification_queue,
                         queue_name_dlq=settings.instant_notification_dlq)

    async def handle_message(self, message: aio_pika.IncomingMessage):

        async with message.process(ignore_processed=True):
            try:
                message_data = json.loads(message.body.decode())
                logging.info(f"Received message: {message_data}")

                content_id = message_data.get("content_id")
                recipient = message_data.get("email")
                message_type = message_data.get("message_type")
                message_transfer = message_data.get("message_transfer")

                # Record the message to the database
                notification_service = await get_notification_service()
                await notification_service.create(
                    content_id=content_id,
                    recipient=recipient,
                    message_type=message_type,
                    message_transfer=message_transfer
                )

            except Exception as e:
                await message.reject(requeue=False)
                logging.error(f"Error handling message: {str(e)}")


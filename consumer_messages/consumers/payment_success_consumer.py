import json
import logging

import aio_pika

from consumer_messages.config.settings import settings
from consumer_messages.consumers.base_consumer import BaseConsumer
from consumer_messages.services.email_service import (
    send_email,
    get_template,
    render_template,
)


class PaymentSuccessConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(
            queue_name=settings.payment_success_queue,
            queue_name_dlq=settings.instant_message_dlq,
        )

    async def handle_message(self, message: aio_pika.IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                message_data = json.loads(message.body.decode())
                logging.info(f"Received message: {message_data}")

                recipient = message_data.get("email")
                message_type = message_data.get("message_type")
                message_transfer = message_data.get("message_transfer")
                content_data = message_data.get("message_data")

                # Retrieve and render the template
                template = get_template(message_type, message_transfer)
                rendered_content = render_template(template, content_data)

                # Send the email
                await send_email(recipient, rendered_content)

            except Exception as e:
                await message.reject(requeue=False)
                logging.error(f"Error handling message: {str(e)}")

import asyncio
import json

import aio_pika
import logging
from consumer_notification_recorder.config.settings import settings


class BaseConsumer:
    def __init__(self, queue_name, queue_name_dlq):
        self.queue_name = queue_name
        self.queue_name_dlq = queue_name_dlq
        self.rabbitmq_url = settings.rabbitmq_connection_url

    async def handle_message(self, message: aio_pika.IncomingMessage):
        """Override this method in subclasses to define message handling."""
        raise NotImplementedError("Subclasses must implement this method")

    async def handle_message_dlq(self, message: aio_pika.IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                message_data = json.loads(message.body.decode())
                logging.info(f"Received message: {message_data}")
                if message.headers['x-death'][0]['count'] > settings.max_retries_dlq:
                    logging.info('after %s retries message canceled', settings.max_retries)
                else:
                    await self.handle_message(message)
            except Exception as e:
                logging.error(f"Error DLQing message: {str(e)}")

    async def start(self):
        connection = await aio_pika.connect_robust(self.rabbitmq_url)
        async with connection:
            channel = await connection.channel()

            queue = await channel.get_queue(self.queue_name)
            queue_name_dlq = await channel.get_queue(self.queue_name_dlq)

            logging.info(f"Waiting for messages on queue: {self.queue_name_dlq}")
            await queue_name_dlq.consume(self.handle_message_dlq)
            logging.info(f"Waiting for messages on queue: {self.queue_name}")
            await queue.consume(self.handle_message)

            await asyncio.Future()

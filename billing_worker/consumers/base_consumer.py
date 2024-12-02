import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractQueue

from billing_worker.config.settings import settings
from billing_worker.dependencies.rabbitmq_connection import rabbitmq_manager


class BaseConsumer:
    def __init__(self, queue_name: str, queue_name_dlq: str):
        self.queue_name = queue_name
        self.queue_name_dlq = queue_name_dlq

    async def handle_message(self, message: aio_pika.IncomingMessage):
        """Override this method in subclasses to define message handling."""
        raise NotImplementedError("Subclasses must implement this method")

    async def handle_message_dlq(self, message: aio_pika.IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                message_data = json.loads(message.body.decode())
                logging.info(f"Received DLQ message: {message_data}")

                x_death = message.headers.get("x-death", [{}])[0]
                retry_count = x_death.get("count", 0)

                if retry_count > settings.max_retries_dlq:
                    logging.warning(
                        f"Message exceeded max retries ({settings.max_retries_dlq}): {message_data}"
                    )
                    # Optionally log or archive messages exceeding retries
                else:
                    await self.handle_message(message)
            except Exception as e:
                logging.error(f"Error processing DLQ message: {str(e)}")

    async def consume_queue(self, queue: AbstractQueue, handler):
        """Helper method to consume a queue with a given handler."""
        logging.info(f"Starting consumption on queue: {queue.name}")
        await queue.consume(handler)

    async def start(self):
        """Start consuming messages using RabbitMQManager."""
        async with rabbitmq_manager.get_channel() as channel:
            queue = await channel.get_queue(self.queue_name)
            queue_dlq = await channel.get_queue(self.queue_name_dlq)

            await asyncio.gather(
                self.consume_queue(queue, self.handle_message),
                self.consume_queue(queue_dlq, self.handle_message_dlq),
            )
            await asyncio.Future()

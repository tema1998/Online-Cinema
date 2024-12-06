from contextlib import asynccontextmanager
from typing import AsyncIterator
import aio_pika

from billing_worker.config.settings import settings


class RabbitMQManager:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.connection: aio_pika.RobustConnection | None = None

    async def connect(self) -> None:
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(self.connection_url)

    async def close(self) -> None:
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

    @asynccontextmanager
    async def get_channel(self) -> AsyncIterator[aio_pika.abc.AbstractChannel]:
        if not self.connection or self.connection.is_closed:
            await self.connect()
        async with self.connection.channel() as channel:
            yield channel


# Singleton instance
rabbitmq_manager = RabbitMQManager(settings.rabbitmq_billing_connection_url)


@asynccontextmanager
async def pika_lifespan():
    """Context manager for RabbitMQ lifespan."""
    await rabbitmq_manager.connect()
    try:
        yield
    finally:
        await rabbitmq_manager.close()

from contextlib import asynccontextmanager

from aio_pika import connect_robust
from aio_pika.abc import AbstractConnection


class ConnectionFactory:
    """
    Factory to manage RabbitMQ connections.
    """

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.connection: AbstractConnection | None = None

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await connect_robust(self.connection_url)

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

    @asynccontextmanager
    async def get_connection(self):
        try:
            await self.connect()
            yield self.connection
        finally:
            await self.close()


class ChannelFactory:
    """
    Factory to manage RabbitMQ channels.
    """

    def __init__(self, connection_factory: ConnectionFactory):
        self.connection_factory = connection_factory

    @asynccontextmanager
    async def get_channel(self):
        async with self.connection_factory.get_connection() as connection:
            async with connection.channel() as channel:
                yield channel

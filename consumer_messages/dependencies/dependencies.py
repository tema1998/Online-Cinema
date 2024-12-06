from contextlib import asynccontextmanager

import aio_pika

from base_config.settings import settings

pika_connection = None


async def set_pika_connection():
    global pika_connection
    pika_connection = await aio_pika.connect_robust(settings.rabbitmq_connection_url)


async def close_pika_connection():
    if pika_connection is not None:
        pika_connection.close()


async def get_rabbitmq_channel():
    channel = await pika_connection.channel()
    try:
        yield channel
    finally:
        await channel.close()


@asynccontextmanager
async def pika_lifespan():
    await set_pika_connection()
    yield
    await close_pika_connection()

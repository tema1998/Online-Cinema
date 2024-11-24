import aio_pika

from consumer_messages.config.settings import settings


async def get_rabbitmq_channel():
    # Set up an asynchronous connection to RabbitMQ
    connection = await aio_pika.connect_robust(settings.rabbitmq_connection_url)
    channel = await connection.channel()
    try:
        yield channel
    finally:
        await channel.close()
        await connection.close()


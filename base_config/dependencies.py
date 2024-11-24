import aio_pika

from base_config.settings import settings

pika_connection = None


async def set_pika_connection():
    global pika_connection
    pika_connection = await aio_pika.connect_robust(settings.rabbitmq_connection_url)


async def close_pika_connection():
    pika_connection.close()


async def get_rabbitmq_channel():
    channel = await pika_connection.channel()
    try:
        yield channel
    finally:
        await channel.close()

# TODO Доделать
# async def get_connection() -> AbstractRobustConnection:
#     return await aio_pika.connect_robust("amqp://guest:guest@localhost/")
#
#
# connection_pool: Pool = Pool(get_connection, max_size=2)
#
#
# async def get_channel() -> aio_pika.Channel:
#     async with connection_pool.acquire() as connection:
#         return await connection.channel()

import aio_pika
from tenacity import retry, stop_after_attempt, wait_fixed

from notification_rabbitmq_init.config.settings import settings


@retry(stop=stop_after_attempt(10), wait=wait_fixed(0.1))
async def rabbitmq_init():
    connection = await aio_pika.connect_robust(settings.rabbitmq_connection_url)
    async with connection:
        channel = await connection.channel()

        await channel.declare_exchange(
            settings.default_exchange, aio_pika.ExchangeType.DIRECT
        )
        await channel.declare_exchange(
            settings.dlx_exchange, aio_pika.ExchangeType.DIRECT
        )

        instant_message_dlq = await channel.declare_queue(
            settings.instant_message_dlq, durable=True
        )
        instant_notification_dlq = await channel.declare_queue(
            settings.instant_notification_dlq, durable=True
        )

        instant_message_queue = await channel.declare_queue(
            settings.instant_message_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx_exchange,
                "x-dead-letter-routing-key": settings.instant_message_dlq,
            },
        )

        scheduled_message_queue = await channel.declare_queue(
            settings.scheduled_message_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx_exchange,
                "x-dead-letter-routing-key": settings.instant_message_dlq,
            },
        )

        instant_notification_queue = await channel.declare_queue(
            settings.instant_notification_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx_exchange,
                "x-dead-letter-routing-key": settings.instant_notification_dlq,
            },
        )

        scheduled_notification_queue = await channel.declare_queue(
            settings.scheduled_notification_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx_exchange,
                "x-dead-letter-routing-key": settings.instant_notification_dlq,
            },
        )

        await instant_message_dlq.bind(
            exchange=settings.dlx_exchange, routing_key=settings.instant_message_dlq
        )
        await instant_notification_dlq.bind(
            exchange=settings.dlx_exchange,
            routing_key=settings.instant_notification_dlq,
        )

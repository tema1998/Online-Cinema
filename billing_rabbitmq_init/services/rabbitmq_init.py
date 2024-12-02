import aio_pika
from tenacity import retry, stop_after_attempt, wait_fixed

from billing_rabbitmq_init.config.settings import settings


@retry(stop=stop_after_attempt(10), wait=wait_fixed(0.1))
async def rabbitmq_init():
    connection = await aio_pika.connect_robust(settings.rabbitmq_billing_connection_url)
    async with connection:
        channel = await connection.channel()

        # Declare exchanges
        await channel.declare_exchange(
            settings.default_exchange_billing, aio_pika.ExchangeType.DIRECT
        )
        await channel.declare_exchange(
            settings.dlx_exchange_billing, aio_pika.ExchangeType.DIRECT
        )

        # Declare Dead Letter Queues (DLQs)
        billing_premium_subscription_success_dlq = await channel.declare_queue(
            settings.billing_premium_subscription_success_dlq, durable=True
        )
        billing_premium_subscription_fail_dlq = await channel.declare_queue(
            settings.billing_premium_subscription_fail_dlq, durable=True
        )
        billing_film_purchase_success_dlq = await channel.declare_queue(
            settings.billing_film_purchase_success_dlq, durable=True
        )
        billing_film_purchase_fail_dlq = await channel.declare_queue(
            settings.billing_film_purchase_fail_dlq, durable=True
        )

        # Declare Primary Queues
        billing_premium_subscription_success_queue = await channel.declare_queue(
            settings.billing_premium_subscription_success_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx_exchange_billing,
                "x-dead-letter-routing-key": settings.billing_premium_subscription_success_dlq,
            },
        )

        billing_premium_subscription_fail_queue = await channel.declare_queue(
            settings.billing_premium_subscription_fail_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx_exchange_billing,
                "x-dead-letter-routing-key": settings.billing_premium_subscription_fail_dlq,
            },
        )

        billing_film_purchase_success_queue = await channel.declare_queue(
            settings.billing_film_purchase_success_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx_exchange_billing,
                "x-dead-letter-routing-key": settings.billing_film_purchase_success_dlq,
            },
        )

        billing_film_purchase_fail_queue = await channel.declare_queue(
            settings.billing_film_purchase_fail_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx_exchange_billing,
                "x-dead-letter-routing-key": settings.billing_film_purchase_fail_dlq,
            },
        )

        # Bind DLQs to the Dead Letter Exchange
        await billing_premium_subscription_success_dlq.bind(
            exchange=settings.dlx_exchange_billing, routing_key=settings.billing_premium_subscription_success_dlq
        )
        await billing_premium_subscription_fail_dlq.bind(
            exchange=settings.dlx_exchange_billing, routing_key=settings.billing_premium_subscription_fail_dlq
        )
        await billing_film_purchase_success_dlq.bind(
            exchange=settings.dlx_exchange_billing, routing_key=settings.billing_film_purchase_success_dlq
        )
        await billing_film_purchase_fail_dlq.bind(
            exchange=settings.dlx_exchange_billing, routing_key=settings.billing_film_purchase_fail_dlq
        )

        # Bind Primary Queues to the Default Exchange
        await billing_premium_subscription_success_queue.bind(
            exchange=settings.default_exchange_billing, routing_key=settings.billing_premium_subscription_success_queue
        )
        await billing_premium_subscription_fail_queue.bind(
            exchange=settings.default_exchange_billing, routing_key=settings.billing_premium_subscription_fail_queue
        )
        await billing_film_purchase_success_queue.bind(
            exchange=settings.default_exchange_billing, routing_key=settings.billing_film_purchase_success_queue
        )
        await billing_film_purchase_fail_queue.bind(
            exchange=settings.default_exchange_billing, routing_key=settings.billing_film_purchase_fail_queue
        )

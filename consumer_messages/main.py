import asyncio
import logging

from consumer_messages.consumers.instant_consumer import InstantConsumer
from consumer_messages.consumers.payment_failed_consumer import PaymentFailedConsumer
from consumer_messages.consumers.payment_success_consumer import PaymentSuccessConsumer
from consumer_messages.dependencies.dependencies import pika_lifespan

logging.basicConfig(level=logging.INFO)


async def main():
    async with pika_lifespan():
        consumers = [
            PaymentSuccessConsumer(),
            InstantConsumer(),
            PaymentFailedConsumer()
        ]

        tasks = [asyncio.create_task(consumer.start())
                 for consumer in consumers]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging

from tenacity import retry, stop_after_attempt, wait_fixed

from billing_worker.consumers.subscription_consumer import SubscriptionSuccessConsumer
from billing_worker.dependencies.rabbitmq_connection import pika_lifespan

logging.basicConfig(level=logging.INFO)

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
async def main():
    async with pika_lifespan():
        consumers = [
            SubscriptionSuccessConsumer(),
        ]

        for consumer in consumers:
            await consumer.start()


if __name__ == "__main__":
    asyncio.run(main())

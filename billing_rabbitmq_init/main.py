import asyncio
import logging

from billing_rabbitmq_init.services.rabbitmq_init import rabbitmq_init

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("RabbitMQ initialization started")
    asyncio.run(rabbitmq_init())
    logging.info("RabbitMQ initialization finished")
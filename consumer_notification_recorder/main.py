import asyncio
import logging

from consumer_notification_recorder.consumers.notification_consumer import NotificationConsumer
from consumer_notification_recorder.config.postgresql import init_db

# from consumers.scheduled_consumer import ScheduledConsumer
# from consumers.notification_consumer import NotificationConsumer

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()
    consumers = [NotificationConsumer()
                 # ScheduledConsumer(),
                 # NotificationConsumer()
                 ]

    for consumer in consumers:
        await consumer.start()

if __name__ == "__main__":
    asyncio.run(main())

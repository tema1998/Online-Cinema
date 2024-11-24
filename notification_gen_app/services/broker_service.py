from abc import ABC, abstractmethod
from enum import Enum
import aio_pika
from fastapi import Depends

from notification_gen_app.api.v1.dependencies import get_rabbitmq_channel


class DeliveryMode(Enum):
    PERSISTENT = aio_pika.DeliveryMode.PERSISTENT
    NON_PERSISTENT = aio_pika.DeliveryMode.NOT_PERSISTENT


class BrokerServiceAbstract(ABC):
    def __init__(self, channel=Depends(get_rabbitmq_channel),
                 delivery_mode=DeliveryMode.PERSISTENT):
        self.channel = channel
        self.delivery_mode = delivery_mode

    @abstractmethod
    async def publish(self, message, queue_name):
        pass


class RabbitMQService(BrokerServiceAbstract):
    async def publish(self, message, queue_name):
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=self.delivery_mode.value
            ),
            routing_key=queue_name
        )

        return {"status": "Message sent to broker", "data": message}

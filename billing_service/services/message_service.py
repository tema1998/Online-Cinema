import datetime
import json
import uuid

from aio_pika import Message, ExchangeType, DeliveryMode
from core.config import config
from dependencies.rabbitmq_connection import ChannelFactory, ConnectionFactory


class MessageSender:
    """
    Responsible for sending messages to a specific exchange and queue.
    """
    def __init__(self, channel_factory: ChannelFactory, exchange_name: str, exchange_type: str = ExchangeType.DIRECT):
        self.channel_factory = channel_factory
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

    async def send_message(self, message: str, routing_key: str):

        def convert_uuid(obj):
            if isinstance(obj, dict):
                return {key: convert_uuid(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_uuid(value) for value in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_uuid(value) for value in obj)
            elif isinstance(obj, set):
                return {convert_uuid(value) for value in obj}
            elif isinstance(obj, uuid.UUID):  # Check if the object is a UUID
                return str(obj)
            elif isinstance(obj, datetime.datetime):  # Check if the object is a datetime
                return obj.isoformat()  # Convert datetime to ISO 8601 string
            return obj
        message_body = json.dumps(convert_uuid(message))
        async with self.channel_factory.get_channel() as channel:
            exchange = await channel.get_exchange(self.exchange_name)
            await exchange.publish(
                Message(body=message_body.encode(), delivery_mode=DeliveryMode.PERSISTENT),
                routing_key=routing_key,
            )
            return {"status": "Message sent", "data": message}


async def get_publisher_service():
    connection_factory = ConnectionFactory(connection_url=config.rabbitmq_billing_connection_url)
    channel_factory = ChannelFactory(connection_factory=connection_factory)
    return MessageSender(channel_factory=channel_factory, exchange_name=config.default_exchange_billing)


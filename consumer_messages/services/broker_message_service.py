import json
import aio_pika
from fastapi import HTTPException

from consumer_messages.dependencies.dependencies import get_rabbitmq_channel


async def send_message_to_broker(message: dict, queue_name: str, persistent: bool = True):
    try:
        # Prepare the message body to be sent to RabbitMQ
        message_body = json.dumps(message)

        # Use async for to retrieve the channel from the async generator
        async for channel in get_rabbitmq_channel():
            # Determine delivery mode based on the `persistent` flag
            delivery_mode = aio_pika.DeliveryMode.PERSISTENT if persistent else aio_pika.DeliveryMode.NON_PERSISTENT

            # Publish the message to the queue
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body.encode(),
                    delivery_mode=delivery_mode
                ),
                routing_key=queue_name
            )

            break  # Exit the loop after using the channel

        return {"status": "Message sent to broker", "data": message_body}

    except Exception as e:
        # ???????????????????????????????????????????????????????????
        raise HTTPException(status_code=500, detail=f"Failed to send message to broker: {str(e)}")

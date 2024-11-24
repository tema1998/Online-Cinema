import json
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import aio_pika

from notification_gen_app.schemas.messages import InstantMessageRequest

class PeriodicMessageService:
    def __init__(self, broker_url:str,  delivery_mode=2):
        self.delivery_mode = delivery_mode
        self.broker_url = broker_url

    async def send_single_message(self, content_id, message: InstantMessageRequest, message_transfer: str, queue_name: str):
        # Create connection to broker, because scheduler doesn't supply dependencies
        connection = await aio_pika.connect_robust(self.broker_url)
        channel = await connection.channel()
        try:

            # Prepare the message body to be sent to RabbitMQ
            message_body = json.dumps({
                "content_id": str(content_id),
                "email": message.email,
                "message_transfer": message_transfer,
                "message_type": "instant",
                "message_data": message.message_data
            })

            # Publish the message to the queue
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body.encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT if self.delivery_mode == 2 else aio_pika.DeliveryMode.NON_PERSISTENT
                ),
                routing_key=queue_name
            )

            return {"status": "Message sent to broker", "data": message_body}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send message to broker: {str(e)}")

        finally:
            await channel.close()
            await connection.close()

class PeriodicTaskService:
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    async def get_tasks(self) -> JSONResponse:
        tasks = []
        for job in self.scheduler.get_jobs():
            tasks.append({"id": job.id, "name": job.name, "interval": str(job.trigger.interval),
                          "start_date": job.trigger.start_date.isoformat(), "timezone": str(job.trigger.timezone),
                          "is_active": False if job.next_run_time is None else True})
        return JSONResponse({'tasks': tasks})

    async def delete_task(self, task_id: str)-> str:
        result = self.scheduler.remove_job(job_id=task_id)
        return str(result)

    async def pause_task(self, task_id: str)-> str:
        result = self.scheduler.pause_job(job_id=task_id)
        return str(result)

    async def resume_task(self, task_id: str)-> str:
        result = self.scheduler.resume_job(job_id=task_id)
        return str(result)

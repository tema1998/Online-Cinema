import aio_pika
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from notification_gen_app.config import scheduler_settings
from notification_gen_app.config.settings import settings
from notification_gen_app.services.periodic_messages import PeriodicTaskService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pika_connection = None


async def set_pika_connection():
    global pika_connection
    pika_connection = await aio_pika.connect_robust(settings.rabbitmq_connection_url)


async def close_pika_connection():
    pika_connection.close()


async def get_rabbitmq_channel():
    channel = await pika_connection.channel()
    try:
        yield channel
    finally:
        await channel.close()


async def get_periodic_task_service():
    task_service = PeriodicTaskService(scheduler=scheduler_settings.scheduler)
    try:
        yield task_service
    finally:
        pass


def get_user_info(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        return {"user_id": user_id, "email": email}

    except PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate token")

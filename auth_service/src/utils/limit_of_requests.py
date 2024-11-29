import datetime
from typing import Optional

from redis.asyncio import Redis

from src.core.config import config

# Установим лимит на 20 запросов в минуту
REQUEST_LIMIT_PER_MINUTE = 20

redis_conn = Redis(host=config.redis_host, port=config.redis_port, db=0)


async def check_limit_of_requests(user_ip: str) -> Optional[bool]:
    """
    Function for checking limit of requests for user's IP.
    If the user has reached limit - return True.
    :param user_ip: IP of user from headers.
    :return: True or None.
    """
    # Create redis pipeline.
    pipe = redis_conn.pipeline()
    now = datetime.datetime.now()

    # Create key user_ip:current_minute
    key = f"{user_ip}:{now.minute}"

    # Add pipline.
    await pipe.incr(key, 1)
    # Set life cycle for key 59 seconds
    await pipe.expire(key, 59)

    # Execute in redis
    result = await pipe.execute()

    # Get result of incr.
    request_number = result[0]

    if request_number > config.limit_of_requests_per_minute:
        return True

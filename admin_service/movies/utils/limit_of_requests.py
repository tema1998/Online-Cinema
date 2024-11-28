import datetime
from typing import Optional

from redis import Redis

from config import settings

redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def check_limit_of_user_requests(user_ip: str) -> Optional[bool]:
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
    key = f'{user_ip}:{now.minute}'

    # Add pipline.
    pipe.incr(key, 1)
    # Set life cycle for key 59 seconds
    pipe.expire(key, 59)

    # Execute in redis
    result = pipe.execute()

    # Get result of incr.
    request_number = result[0]

    if request_number > settings.LIMIT_OF_REQUESTS_PER_MINUTE:
        return True

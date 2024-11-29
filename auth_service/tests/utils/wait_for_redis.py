import logging

from redis import Redis
from redis.exceptions import RedisError

from tests.settings import Settings
from tests.utils.backoff import backoff

settings = Settings()

logger = logging.getLogger("log")


@backoff(limit_of_retries=0)
def wait_for_redis():
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    ping = redis_client.ping()
    if ping:
        return ping
    raise RedisError


if __name__ == "__main__":
    wait_for_redis()

from typing import Optional

from redis.asyncio import Redis

from src.core.config import config

redis: Optional[Redis] = None


# Function to initialize the Redis connection using aioredis (now part of redis-py)
async def init_redis() -> Redis:
    global redis
    redis = Redis(host=config.redis_host, port=config.redis_port)
    return redis


# Function to get the Redis connection
async def get_redis() -> Redis:
    if redis is None:
        raise RuntimeError("Redis has not been initialized")
    return redis


# To close the redis connection when shutting down
async def close_redis():
    global redis
    if redis:
        await redis.close()
        redis = None

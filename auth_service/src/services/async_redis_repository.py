from typing import Any, Optional, List

from redis.asyncio import Redis


class AsyncRedisRepository:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        if expire:
            return await self.redis.setex(key, expire, value)
        return await self.redis.set(key, value)

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        if value is None:
            return None
        return value.decode("utf-8")

    async def delete(self, key: str) -> bool:
        return await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key) > 0

    async def expire(self, key: str, time: int) -> bool:
        return await self.redis.expire(key, time)

    async def flushdb(self) -> bool:
        return await self.redis.flushdb()

    async def keys(self, pattern: str = "*") -> List[str]:
        keys = await self.redis.keys(pattern)
        return [key.decode("utf-8") for key in keys]

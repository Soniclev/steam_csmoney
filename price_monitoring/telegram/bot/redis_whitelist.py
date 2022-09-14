from aioredis import Redis

from .abstract_whitelist import AbstractWhitelist


class RedisWhitelist(AbstractWhitelist):
    def __init__(self, redis: Redis, key: str):
        self._redis = redis
        self._key = key

    async def add_member(self, member: int) -> None:
        await self._redis.sadd(self._key, member)

    async def remove_member(self, member: int) -> None:
        await self._redis.srem(self._key, member)

    async def get_members(self) -> list[int]:
        members = await self._redis.smembers(self._key)
        return [int(x) for x in members]

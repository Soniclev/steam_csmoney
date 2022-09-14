from aioredis import Redis

from .abstract_settings import AbstractSettings
from ..models import NotificationSettings


class RedisSettings(AbstractSettings):
    def __init__(self, redis: Redis, key: str):
        self._redis = redis
        self._key = key

    async def get(self) -> NotificationSettings | None:
        value = await self._redis.get(self._key)
        if value:
            return NotificationSettings.load_bytes(value)
        return None

    async def set(self, settings: NotificationSettings) -> None:
        await self._redis.set(self._key, settings.dumps())

    async def set_default(self) -> None:
        await self._redis.setnx(self._key, NotificationSettings().dumps())

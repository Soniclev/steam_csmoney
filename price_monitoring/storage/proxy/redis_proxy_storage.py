from aioredis import Redis

from proxy_http.proxy import Proxy
from .abstract_proxy_storage import AbstractProxyStorage


class RedisProxyStorage(AbstractProxyStorage):
    def __init__(self, redis: Redis, key: str):
        self._redis = redis
        self._key = key

    async def add(self, proxy: Proxy) -> None:
        await self._redis.sadd(self._key, proxy.dumps())

    async def get_all(self) -> list[Proxy]:
        return [Proxy.load_bytes(x) for x in await self._redis.smembers(self._key)]

    async def remove(self, proxy: Proxy) -> None:
        await self._redis.srem(self._key, proxy.dumps())

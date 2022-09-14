from aioredis import Redis

from .abstract_name_resolver import AbstractNameResolver, SkinNotFoundError
from ....types import MarketName, ItemNameId

_KEY = "steam_name_id_cache"


class RedisCachedNameResolver(AbstractNameResolver):
    def __init__(self, resolver: AbstractNameResolver, redis: Redis):
        self._resolver = resolver
        self._redis = redis

    async def resolve_market_name(self, market_name: MarketName) -> ItemNameId:
        resp = await self._redis.hget(_KEY, market_name)
        if resp:
            name_id = int(resp.decode())
        else:
            try:
                name_id = await self._resolver.resolve_market_name(market_name)
            except SkinNotFoundError:
                name_id = -1
            await self._redis.hset(_KEY, market_name, name_id)
        if name_id == -1:
            raise SkinNotFoundError(market_name)
        return name_id

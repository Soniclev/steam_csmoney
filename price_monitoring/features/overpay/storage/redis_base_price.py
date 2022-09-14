from datetime import timedelta

from aioredis import Redis

from .abstract_base_price import AbstractBasePriceStorage
from ....types import MarketName

_BASE_PRICE_TTL = timedelta(hours=12)


def _pattern() -> str:
    return "base_price:csmoney:*"


def _key(market_name: str) -> str:
    return f"base_price:csmoney:{market_name}"


def _extract_market_name(key: str) -> MarketName:
    market_name = key.rsplit(":", 1)[1]
    return market_name


class RedisBasePriceStorage(AbstractBasePriceStorage):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def update_item(self, market_name: MarketName, base_price: float):
        key = _key(market_name)
        await self._redis.set(key, str(base_price), ex=_BASE_PRICE_TTL)

    async def get_all(self) -> dict[MarketName, float]:
        pattern = _pattern()
        keys = await self._redis.keys(pattern)
        values = await self._redis.mget(keys)
        result = {}
        for key, value in zip(keys, values):
            if not value:
                continue  # pragma: no cover
            base_price = float(value.decode())
            market_name = _extract_market_name(key.decode())
            result[market_name] = base_price
        return result

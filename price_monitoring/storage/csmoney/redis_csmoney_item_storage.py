from datetime import timedelta

from aioredis import Redis

from common.tracer import trace, annotate
from .abstract_csmoney_item_storage import AbstractCsmoneyItemStorage
from ...types import MarketName

_ITEM_TTL = timedelta(minutes=60)


def _pattern(prefix: str, market_name: MarketName) -> str:
    return f"{prefix}{market_name}:*"


def _key(prefix: str, market_name: MarketName, price: float) -> str:
    return f"{prefix}{market_name}:{price}"


def _extract_market_name(key: str, full_key: str) -> MarketName:
    suffix = full_key.removeprefix(key)
    market_name = suffix.rsplit(":", maxsplit=1)[0]
    return market_name


def _extract_price(prefix: str, full_key: str) -> float:
    suffix = full_key.removeprefix(prefix)
    price = suffix.rsplit(":", maxsplit=1)[-1]
    return float(price)


class RedisCsmoneyItemStorage(AbstractCsmoneyItemStorage):
    def __init__(self, redis: Redis, prefix: str, trade_ban: bool):
        self._redis = redis
        self._prefix = prefix
        self._trade_ban = trade_ban

    async def update_item(self, market_name: MarketName, item_price: float) -> None:
        key = _key(self._prefix, market_name, item_price)
        await self._redis.set(key, 1, ex=_ITEM_TTL)

    @trace
    async def get_all(self) -> dict[MarketName, float]:
        pattern = _pattern(self._prefix, "*")
        keys = [x.decode() for x in await self._redis.keys(pattern)]
        annotate(f"Loaded {len(keys)} from redis")
        result = {}
        for key in keys:
            market_name = _extract_market_name(self._prefix, key)
            price = _extract_price(self._prefix, key)
            if market_name not in result:
                result[market_name] = price
            elif result[market_name] > price:
                result[market_name] = price
        return result

    @property
    def is_trade_ban(self) -> bool:
        return self._trade_ban

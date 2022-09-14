from datetime import timedelta

from aioredis import Redis

from .abstract_overpay import AbstractOverpayStorage
from ....models.csmoney import CsmoneyItemOverpay

_OVERPAY_ITEM_TTL = timedelta(days=7)


def _pattern() -> str:
    return "overpay:csmoney:*:*"


def _key(market_name: str, float_: str) -> str:
    return f"overpay:csmoney:{market_name}:{float_}"


class RedisOverpayStorage(AbstractOverpayStorage):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def add_overpay(self, item_overpay: CsmoneyItemOverpay):
        key = _key(item_overpay.market_name, item_overpay.float_)
        data = item_overpay.dump_bytes()
        await self._redis.set(key, data, ex=_OVERPAY_ITEM_TTL)

    async def get_all(self) -> list[CsmoneyItemOverpay]:
        pattern = _pattern()
        keys = await self._redis.keys(pattern)
        values = await self._redis.mget(keys)
        result = [CsmoneyItemOverpay.load_bytes(value) for value in values if value]
        return result

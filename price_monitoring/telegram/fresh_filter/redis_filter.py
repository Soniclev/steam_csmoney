import asyncio
from datetime import timedelta
from typing import Sequence

from aioredis import Redis

from .abstract_filter import AbstractFilter
from ..offers import BaseItemOffer

_ENTRY_TTL = timedelta(minutes=30)


def _key(market_name: str, percent_diff: float) -> str:
    return f"cache:withdraw:{market_name}:{percent_diff}"


class RedisFilter(AbstractFilter):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def filter_new_offers(self, offers: Sequence[BaseItemOffer]) -> Sequence[BaseItemOffer]:
        keys = [_key(offer.market_name, offer.compute_percentage()) for offer in offers]
        values = await self.redis.mget(keys)
        result = []
        for offer, value in zip(offers, values):
            if not value:
                result.append(offer)
        return result

    async def append_offers(self, offers: Sequence[BaseItemOffer]) -> None:
        tasks = []  # type: ignore
        for offer in offers:
            key = _key(offer.market_name, offer.compute_percentage())
            tasks.append(self.redis.set(key, 1, ex=_ENTRY_TTL))
        await asyncio.gather(*tasks)

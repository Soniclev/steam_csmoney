from datetime import timedelta

from aioredis import Redis

from common.tracer import trace, annotate
from .abstract_steam_sell_history_storage import AbstractSteamSellHistoryStorage
from ...models.steam import SkinSellHistory
from ...types import MarketName

_ITEM_TTL = timedelta(hours=18)


def _pattern(market_name: MarketName) -> str:
    return f"sell_history:steam:{market_name}"


def _key(market_name: MarketName) -> str:
    return f"sell_history:steam:{market_name}"


def _extract_market_name(key: str) -> MarketName:
    parts = key.split(":", 2)
    market_name = parts[-1]
    return market_name


class RedisSteamSellHistoryStorage(AbstractSteamSellHistoryStorage):
    def __init__(self, redis: Redis):
        self._redis = redis

    @trace
    async def get_all(self) -> dict[MarketName, SkinSellHistory]:
        pattern = _pattern("*")
        keys = [x.decode() for x in await self._redis.keys(pattern)]
        annotate(f"Loaded {len(keys)} keys")
        values = await self._redis.mget(keys)
        annotate(f"Loaded {len(values)} keys")
        return {
            _extract_market_name(key): SkinSellHistory.load_bytes(value)
            for key, value in zip(keys, values)
            if value
        }

    async def update_skin(self, history: SkinSellHistory) -> None:
        key = _key(history.market_name)
        value = history.dump_bytes()
        await self._redis.set(key, value, ex=_ITEM_TTL)

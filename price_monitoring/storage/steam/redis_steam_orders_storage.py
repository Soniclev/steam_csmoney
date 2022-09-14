from datetime import timedelta

from aioredis import Redis

from common.tracer import trace, annotate
from .abstract_steam_orders_storage import AbstractSteamOrdersStorage
from ...types import MarketName, BuySellOrders, OrderPrice

_ITEM_TTL = timedelta(hours=4)


def _pattern(market_name: MarketName) -> str:
    return f"prices:steam:{market_name}"


def _key(market_name: MarketName) -> str:
    return f"prices:steam:{market_name}"


def _value(buy_order: OrderPrice, sell_order: OrderPrice) -> str:
    return f"{buy_order}:{sell_order}"


def _extract_market_name(key: str) -> MarketName:
    parts = key.split(":", 2)
    market_name = parts[-1]
    return market_name


def _extract_orders(key: str) -> BuySellOrders:
    parts = key.split(":")
    buy = parts[-2]
    sell = parts[-1]
    buy = None if buy == "None" else float(buy)
    sell = None if sell == "None" else float(sell)
    return buy, sell


class RedisSteamOrdersStorage(AbstractSteamOrdersStorage):
    def __init__(self, redis: Redis):
        self._redis = redis

    @trace
    async def get_all(self) -> dict[MarketName, BuySellOrders]:
        pattern = _pattern("*")
        keys = [x.decode() for x in await self._redis.keys(pattern)]
        annotate(f"Loaded {len(keys)} keys")
        values = [x.decode() if x else None for x in await self._redis.mget(keys)]
        annotate(f"Loaded {len(values)} values")
        return {
            _extract_market_name(key): _extract_orders(value)
            for key, value in zip(keys, values)
            if value
        }

    async def update_skin_order(
        self, market_name: MarketName, buy_order: OrderPrice, sell_order: OrderPrice
    ) -> None:
        key = _key(market_name)
        value = _value(buy_order, sell_order)
        await self._redis.set(key, value, ex=_ITEM_TTL)

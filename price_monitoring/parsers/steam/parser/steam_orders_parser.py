import logging

from aiohttp import ClientSession

from proxy_http.async_proxies_concurrent_limiter import AsyncSessionConcurrentLimiter
from proxy_http.decorators import catch_aiohttp
from .abstract_steam_orders_parser import AbstractSteamOrdersParser
from ..name_resolver import AbstractNameResolver, SkinNotFoundError
from ....models.steam import SteamSkinHistogram
from ....queues import AbstractSteamOrderWriter
from ....types import ItemNameId, MarketName

_RESPONSE_TIMEOUT = 5
_POSTPONE_DURATION = 3
logger = logging.getLogger(__name__)


# noinspection SpellCheckingInspection
def _create_url(name_id: ItemNameId) -> str:
    return (
        f"https://steamcommunity.com/market/itemordershistogram?country=BY"
        f"&language=english&currency=1&item_nameid={name_id}&two_factor=0"
    )


@catch_aiohttp(logger)
async def _request(session: ClientSession, url: str) -> dict | None:
    async with session.get(url, timeout=_RESPONSE_TIMEOUT) as response:
        response.raise_for_status()
        return await response.json()


class SteamOrdersParser(AbstractSteamOrdersParser):
    def __init__(
        self,
        limiter: AsyncSessionConcurrentLimiter,
        name_resolver: AbstractNameResolver,
    ):
        self._limiter = limiter
        self._name_resolver = name_resolver

    # the result of function reflect success of fetching
    async def fetch_orders(
        self, market_name: MarketName, result_queue: AbstractSteamOrderWriter
    ) -> bool:
        try:
            name_id = await self._name_resolver.resolve_market_name(market_name)
        except SkinNotFoundError:
            return True
        url = _create_url(name_id)
        session = await self._limiter.get_available(_POSTPONE_DURATION)

        data = await _request(session, url)
        if not data:
            return False
        try:
            assert "success" in data
            assert data["success"] == 1

            skin = SteamSkinHistogram(market_name=market_name, response=data)
            await result_queue.put(skin)
            logger.info(f"Successfully got histogram for {market_name}")
            return True
        except AssertionError:
            logger.info(f"Failed to get histogram for {market_name}")
            return False

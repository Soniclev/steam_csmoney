import re

from proxy_http.async_proxies_concurrent_limiter import AsyncSessionConcurrentLimiter
from .abstract_name_resolver import AbstractNameResolver, SkinNotFoundError
from ....types import MarketName, ItemNameId

_RESPONSE_TIMEOUT = 15
_NAME_RESOLVE_POSTPONE_DURATION = 30


def _generate_steam_market_url(market_name: MarketName) -> str:
    return f"https://steamcommunity.com/market/listings/730/{market_name}"


class NameResolver(AbstractNameResolver):
    def __init__(self, limiter: AsyncSessionConcurrentLimiter):
        self._limiter = limiter

    async def resolve_market_name(self, market_name: MarketName) -> ItemNameId:
        session = await self._limiter.get_available(_NAME_RESOLVE_POSTPONE_DURATION)
        url = _generate_steam_market_url(market_name)
        cookies = {}  # type: ignore
        async with session.get(url, cookies=cookies, timeout=_RESPONSE_TIMEOUT) as response:
            response.raise_for_status()
            text = await response.text()
            item_nameid = re.findall(r"Market_LoadOrderSpread\(\s*(\d*)\s*\);", text)
            if item_nameid:
                return int(item_nameid[0])
            elif "var g_rgListingInfo = [];" in text:
                raise SkinNotFoundError(market_name)
            else:
                raise ValueError(text)

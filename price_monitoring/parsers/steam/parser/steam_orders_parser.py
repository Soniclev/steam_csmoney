import asyncio
import logging
from datetime import datetime, timedelta
import urllib.parse

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


# itemordershistogram 429 abuse from here:
# https://gist.github.com/Soniclev/981f8adbc7c6a68350aff9e2a877ed1e
@catch_aiohttp(logger)
async def _request(session: ClientSession, url: str, app_id: int, market_hash_name: str) -> dict | None:
    time_now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    headers = {
        'Origin': "steamcommunity.com",
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f"https://steamcommunity.com/market/listings/{app_id}/{urllib.parse.quote(market_hash_name)}",
        'If-Modified-Since': time_now,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    for _ in range(5):
        async with session.get(url, headers=headers, timeout=_RESPONSE_TIMEOUT) as response:
            response.raise_for_status()
            if response.status == 200:
                return await response.json()
            elif response.status == 304:
                headers["If-Modified-Since"] = response.headers["Last-Modified"]
                date = response.headers["Date"]
                date_dt = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT')
                expires = response.headers["Expires"]
                expires_dt = datetime.strptime(expires, '%a, %d %b %Y %H:%M:%S GMT')
                if expires_dt > date_dt:
                    sleep = expires_dt - date_dt
                    if sleep < timedelta(seconds=5):
                        sleep = timedelta(seconds=5)
                else:
                    sleep = timedelta(seconds=5)
                await asyncio.sleep(sleep.total_seconds())
            else:
                raise ValueError(f"Unsupported response: {response.status}")


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

        # app_id is hardcoded(
        data = await _request(session, url, app_id=730, market_hash_name=market_name)
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

import logging
import re

from aiohttp import ClientSession

from proxy_http.async_proxies_concurrent_limiter import AsyncSessionConcurrentLimiter
from proxy_http.decorators import catch_aiohttp
from .abstract_sell_history_parser import AbstractSellHistoryParser
from ....models.steam import SteamSellHistory
from ....queues import AbstractSteamSellHistoryWriter
from ....types import MarketName

_RESPONSE_TIMEOUT = 10
_POSTPONE_DURATION = 30
logger = logging.getLogger(__name__)


_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        # 'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        # 'Referer': referer,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        # 'If-Modified-Since': time_now
    }


# noinspection SpellCheckingInspection
def _create_url(market_name: MarketName) -> str:
    return f"https://steamcommunity.com/market/listings/730/{market_name}"


@catch_aiohttp(logger)
async def _request(session: ClientSession, url: str) -> str | None:
    async with session.get(url, headers=_headers, timeout=_RESPONSE_TIMEOUT) as response:
        response.raise_for_status()
        return await response.text()


class SteamSellHistoryParser(AbstractSellHistoryParser):
    def __init__(self, limiter: AsyncSessionConcurrentLimiter):
        self._limiter = limiter

    async def fetch_history(
        self, market_name: MarketName, result_queue: AbstractSteamSellHistoryWriter
    ) -> bool:
        url = _create_url(market_name)
        session = await self._limiter.get_available(_POSTPONE_DURATION)

        page = await _request(session, url)
        if not page:
            return False
        try:
            encoded_data = re.findall(r"\s+var line1=([^;]+);", page)[0]
        except IndexError:
            logger.info(f"There is not sell history for {market_name}")
            return True

        history = SteamSellHistory(market_name=market_name, encoded_data=encoded_data)
        await result_queue.put(history)
        logger.info(f"Successfully got sell history for {market_name}")
        return True

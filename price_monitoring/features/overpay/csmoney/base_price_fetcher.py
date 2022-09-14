import logging

from aiohttp import ClientSession

from proxy_http.async_proxies_concurrent_limiter import AsyncSessionConcurrentLimiter
from proxy_http.decorators import catch_aiohttp
from .abstract_base_price_fetcher import AbstractBasePriceFetcher
from ....types import NameId

_POSTPONE_DURATION = 10
_REQUEST_TIMEOUT = 7

logger = logging.getLogger()


def _headers():
    return {
        "Origin": "https://wiki.cs.money",
        "Referer": "https://wiki.cs.money/weapons/desert-eagle/trigger-discipline",
        "Alt-Used": "wiki.cs.money",
        "content-type": "application/json",
    }


def _gen_payload(name_ids: list[int]) -> dict:
    return {
        "operationName": "price_trader_log",
        "variables": {"name_ids": name_ids},
        "query": "query price_trader_log($name_ids: [Int!]!) "
        "{\n"
        "  price_trader_log(input: {name_ids: $name_ids}) "
        "{\n"
        "    name_id\n"
        "    values {\n"
        "      price_trader_new\n"
        "      time\n"
        "    }\n"
        "  }\n"
        "}",
    }


@catch_aiohttp(logger)
async def _request(session: ClientSession, payload: dict) -> dict:
    async with session.post(
        "https://wiki.cs.money/graphql",
        json=payload,
        timeout=_REQUEST_TIMEOUT,
        headers=_headers(),
    ) as response:
        response.raise_for_status()
        return await response.json()


class BasePriceFetcher(AbstractBasePriceFetcher):
    def __init__(self, csmoney_limiter: AsyncSessionConcurrentLimiter):
        self._csmoney_limiter = csmoney_limiter

    async def get(self, name_ids: list[NameId]) -> dict[NameId, float]:
        if not name_ids:
            return {}
        session = await self._csmoney_limiter.get_available(_POSTPONE_DURATION)
        payload = _gen_payload(name_ids)
        result = await _request(session, payload)
        if not result:
            raise ValueError(f"There is not base prices for {name_ids=}")
        try:
            data = result["data"]["price_trader_log"]
            data = {obj["name_id"]: obj["values"][-1]["price_trader_new"] for obj in data}
            return {name_id: price for name_id, price in data.items() if name_id in name_ids}
        except Exception as exc:
            raise ValueError("Failed to parse response from wiki.cs.money") from exc

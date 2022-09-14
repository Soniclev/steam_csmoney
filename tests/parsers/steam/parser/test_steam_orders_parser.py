import asyncio
from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from price_monitoring.models.steam import SteamSkinHistogram
from price_monitoring.parsers.steam.name_resolver.abstract_name_resolver import SkinNotFoundError
from price_monitoring.parsers.steam.parser.steam_orders_parser import SteamOrdersParser


def steam_histogram_success_response():
    return {"success": 1, "buy": 100, "foo": "bar"}


def steam_histogram_invalid_response_1():
    return {
        "success": 104,
    }


def steam_histogram_invalid_response_2():
    return "null"


@pytest.fixture()
def steam_histogram():
    return SteamSkinHistogram(market_name="AK47", response=steam_histogram_success_response())


@pytest.fixture()
async def limiter_fixture():
    session = ClientSession()
    m = AsyncMock()
    m.get_available.return_value = session
    yield m
    await session.close()


@pytest.fixture()
def result_queue_fixture():
    return AsyncMock()


@pytest.fixture()
def name_resolver():
    resolver = AsyncMock()
    resolver.resolve_market_name.return_value = 123
    return resolver


@pytest.fixture()
def steam_impl(limiter_fixture, name_resolver):
    return SteamOrdersParser(limiter_fixture, name_resolver)


async def test_parse__assert_response(
    steam_impl, name_resolver, result_queue_fixture, steam_histogram
):
    with aioresponses() as m:
        m.get(
            "https://steamcommunity.com/market/itemordershistogram?country=BY"
            "&language=english&currency=1&item_nameid=123&two_factor=0",
            payload=steam_histogram_success_response(),
        )
        result = await steam_impl.fetch_orders("AK47", result_queue_fixture)

    assert result
    assert result_queue_fixture.put.call_count == 1
    for call in result_queue_fixture.put.call_args_list:
        assert call.args == (steam_histogram,)


@pytest.mark.parametrize(
    "payload",
    [
        steam_histogram_invalid_response_1(),
        steam_histogram_invalid_response_2(),
    ],
)
async def test_parse__assert_invalid_response(
    steam_impl, result_queue_fixture, steam_histogram, payload
):
    with aioresponses() as m:
        m.get(
            "https://steamcommunity.com/market/itemordershistogram?country=BY"
            "&language=english&currency=1&item_nameid=123&two_factor=0",
            payload=payload,
        )
        result = await steam_impl.fetch_orders("AK47", result_queue_fixture)

    assert not result
    assert result_queue_fixture.put.call_count == 0


async def test_parse__assert_call(steam_impl, result_queue_fixture, steam_histogram):
    with aioresponses() as m:
        m.get(
            "https://steamcommunity.com/market/itemordershistogram?country=BY"
            "&language=english&currency=1&item_nameid=123&two_factor=0",
            payload=steam_histogram_success_response(),
        )
        await steam_impl.fetch_orders("AK47", result_queue_fixture)

    assert len(m.requests) == 1
    urls = {str(url): len(calls) for (_, url), calls in m.requests.items()}

    # asserting number of calls for each URL
    assert (
        urls[
            "https://steamcommunity.com/market/itemordershistogram?country=BY&currency=1"
            "&item_nameid=123&language=english&two_factor=0"
        ]
        == 1
    )


async def test_parse__non_existed_skin(steam_impl, name_resolver, result_queue_fixture):
    name_resolver.resolve_market_name.side_effect = SkinNotFoundError("AK47")

    with aioresponses() as m:
        m.get(
            "https://steamcommunity.com/market/itemordershistogram?country=BY"
            "&language=english&currency=1&item_nameid=123&two_factor=0",
            payload=steam_histogram_success_response(),
        )
        result = await steam_impl.fetch_orders("AK47", result_queue_fixture)

    assert result
    assert len(m.requests) == 0
    assert result_queue_fixture.put.call_count == 0


@pytest.mark.parametrize(
    "error",
    [
        aiohttp.ClientProxyConnectionError(None, OSError()),
        asyncio.exceptions.TimeoutError(),
        ConnectionResetError(),
    ],
)
async def test_parse__network_error(steam_impl, result_queue_fixture, error):
    with aioresponses() as m:
        m.get(
            "https://steamcommunity.com/market/itemordershistogram?country=BY"
            "&language=english&currency=1&item_nameid=123&two_factor=0",
            exception=error,
        )
        result = await steam_impl.fetch_orders("AK47", result_queue_fixture)

    assert not result
    assert len(m.requests) == 1
    assert result_queue_fixture.put.call_count == 0


if __name__ == "__main__":
    pytest.main()

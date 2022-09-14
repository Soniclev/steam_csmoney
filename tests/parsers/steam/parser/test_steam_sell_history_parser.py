import asyncio
from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from price_monitoring.models.steam import SteamSellHistory
from price_monitoring.parsers.steam.parser.steam_sell_history_parser import SteamSellHistoryParser

_SUCCESS_RESPONSE = """$J(document).ready(function(){
            var line1=[["Jan 21 2022 01: +0",10.675,"76680"]];
            g_timePriceHistoryEarliest = new Date();
            """

_ENCODED_DATA = '[["Jan 21 2022 01: +0",10.675,"76680"]]'
_EXPECTED = SteamSellHistory(market_name="AK47", encoded_data=_ENCODED_DATA)


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
def parser(limiter_fixture):
    return SteamSellHistoryParser(limiter_fixture)


async def test_parse__assert_response(parser, result_queue_fixture):
    with aioresponses() as m:
        m.get(
            "https://steamcommunity.com/market/listings/730/AK47",
            body=_SUCCESS_RESPONSE,
        )
        result = await parser.fetch_history("AK47", result_queue_fixture)

    assert result
    result_queue_fixture.put.assert_awaited_once_with(_EXPECTED)


@pytest.mark.parametrize(
    "body, is_ok",
    [
        ("null", True),
        ("asdvasdvasdbewtwbw", True),
        ("", False),
    ],
)
async def test_parse__assert_invalid_response(parser, result_queue_fixture, body, is_ok):
    with aioresponses() as m:
        m.get("https://steamcommunity.com/market/listings/730/AK47", body=body)
        result = await parser.fetch_history("AK47", result_queue_fixture)

    assert result == is_ok
    result_queue_fixture.put.assert_not_called()


@pytest.mark.parametrize(
    "error",
    [
        aiohttp.ClientProxyConnectionError(None, OSError()),
        asyncio.exceptions.TimeoutError(),
        ConnectionResetError(),
    ],
)
async def test_parse__network_error(parser, result_queue_fixture, error):
    with aioresponses() as m:
        m.get("https://steamcommunity.com/market/listings/730/AK47", exception=error)
        result = await parser.fetch_history("AK47", result_queue_fixture)

    assert not result
    assert len(m.requests) == 1
    result_queue_fixture.put.assert_not_called()

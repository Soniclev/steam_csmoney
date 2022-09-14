from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from price_monitoring.features.overpay.csmoney.base_price_fetcher import (
    _gen_payload,
    _headers,
    BasePriceFetcher,
)


def test_gen_payload():
    assert _gen_payload([1, 2, 3, 4, 5]) == {
        "operationName": "price_trader_log",
        "variables": {"name_ids": [1, 2, 3, 4, 5]},
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


def test_correct_content_type():
    assert _headers()["content-type"] == "application/json"


@pytest.fixture()
async def limiter_fixture():
    session = ClientSession()
    m = AsyncMock()
    m.get_available.return_value = session
    yield m
    await session.close()


@pytest.fixture()
def price_fetcher(limiter_fixture):
    return BasePriceFetcher(limiter_fixture)


RESPONSE = {
    "data": {
        "price_trader_log": [
            {
                "name_id": 13269,
                "values": [
                    {"price_trader_new": 1594.6, "time": 1520899200},
                    {"price_trader_new": 6919.57, "time": 1650326400},
                ],
            },
            {
                "name_id": 12345,
                "values": [
                    {"price_trader_new": 1234.5, "time": 1520899200},
                    {"price_trader_new": 6789.1, "time": 1650326400},
                ],
            },
        ]
    }
}


async def test_correct_content_type_2(price_fetcher):
    with aioresponses() as m:
        m.post("https://wiki.cs.money/graphql", payload=RESPONSE)
        await price_fetcher.get([13269])

    for call in list(m.requests.values())[0]:
        assert call.kwargs["headers"]["content-type"] == "application/json"


async def test_correct_payload(price_fetcher):
    with aioresponses() as m:
        m.post("https://wiki.cs.money/graphql", payload=RESPONSE)
        await price_fetcher.get([13269, 12345])

    for call in list(m.requests.values())[0]:
        assert call.kwargs["json"] == _gen_payload([13269, 12345])


@pytest.mark.parametrize(
    "expected", [{}, {13269: 6919.57}, {12345: 6789.1}, {13269: 6919.57, 12345: 6789.1}]
)
async def test_response(price_fetcher, expected):
    with aioresponses() as m:
        m.post("https://wiki.cs.money/graphql", payload=RESPONSE)
        prices = await price_fetcher.get(list(expected.keys()))

    assert prices == expected


async def test_invalid_response(price_fetcher):
    with aioresponses() as m:
        m.post("https://wiki.cs.money/graphql", payload={"data": {}})
        with pytest.raises(ValueError):
            await price_fetcher.get([13269])
    with aioresponses() as m:
        m.post("https://wiki.cs.money/graphql", exception=aiohttp.ClientConnectionError())
        with pytest.raises(ValueError):
            await price_fetcher.get([13269])

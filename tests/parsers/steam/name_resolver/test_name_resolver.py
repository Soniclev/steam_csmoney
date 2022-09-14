from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from price_monitoring.parsers.steam.name_resolver.abstract_name_resolver import SkinNotFoundError
from price_monitoring.parsers.steam.name_resolver.name_resolver import NameResolver


def response_with_name_id():
    with open("tests/parsers/steam/name_resolver/response_with_name_id.txt", encoding="utf8") as f:
        return f.read()


def response_of_non_existed_item():
    with open(
        "tests/parsers/steam/name_resolver/response_of_non_existed_item.txt",
        encoding="utf8",
    ) as f:
        return f.read()


@pytest.fixture()
async def limiter_fixture():
    session = ClientSession()
    m = AsyncMock()
    m.get_available.return_value = session
    yield m
    await session.close()


@pytest.fixture()
def resolver(limiter_fixture):
    return NameResolver(limiter_fixture)


async def test_resolve(resolver):
    with aioresponses() as m:
        m.get(
            "https://steamcommunity.com/market/listings/730/AK47",
            payload=response_with_name_id(),
        )
        name_id = await resolver.resolve_market_name("AK47")

    assert name_id == 175880636


async def test_resolve__skin_do_not_exist(resolver):
    with aioresponses() as m:
        m.get(
            "https://steamcommunity.com/market/listings/730/AK47",
            payload=response_of_non_existed_item(),
        )
        with pytest.raises(SkinNotFoundError):
            await resolver.resolve_market_name("AK47")


@pytest.mark.parametrize("response", ["", "null", "<html></html>"])
async def test_resolve__invalid_input(resolver, response):
    with aioresponses() as m:
        m.get("https://steamcommunity.com/market/listings/730/AK47", payload=response)
        with pytest.raises(ValueError):
            await resolver.resolve_market_name("AK47")


if __name__ == "__main__":
    pytest.main()

from unittest import mock
from unittest.mock import AsyncMock

import pytest

from price_monitoring.telegram.offer_provider.redis_provider import RedisOfferProvider


@pytest.fixture
def steam():
    return AsyncMock()


@pytest.fixture
def csmoney():
    return AsyncMock()


@pytest.fixture
def provider(steam, csmoney):
    return RedisOfferProvider(steam, csmoney)


@pytest.mark.parametrize("steam_item", [{"AK": (100, 200)}, {"AK": (None, 200)}, {}])
@pytest.mark.parametrize("csmoney_item", [{"AK": 125}, {}])
async def test_get_items__existence(steam, csmoney, provider, steam_item, csmoney_item):
    steam.get_all.return_value = steam_item
    csmoney.get_all.return_value = csmoney_item

    items = await provider.get_items(-100, 50)
    should = True
    if not steam_item:
        should = False
    if steam_item and not steam_item["AK"][0]:
        should = False
    if not csmoney_item:
        should = False

    assert len(items) == should


@pytest.mark.parametrize("percentage_limit", [5, 0, -24, -25, -26, None])
async def test_get_items__percentage_limit(steam, csmoney, provider, percentage_limit):
    steam.get_all.return_value = {"AK": (75, None)}
    csmoney.get_all.return_value = {"AK": 100}

    with mock.patch("price_monitoring.telegram.offers.SteamOrdersOffer.compute_percentage") as m:
        m.return_value = -25
        items = await provider.get_items(percentage_limit, 50)

    should = -25 >= percentage_limit if percentage_limit is not None else True
    assert len(items) == should


async def test_get_items__percentage_limit_equal_zero(steam, csmoney, provider):
    percentage_limit = 0
    steam.get_all.return_value = {"AK": (75, None)}
    csmoney.get_all.return_value = {"AK": 100}

    with mock.patch("price_monitoring.telegram.offers.SteamOrdersOffer.compute_percentage") as m:
        m.return_value = -1
        items = await provider.get_items(percentage_limit, 50)

    should = False
    assert len(items) == should


@pytest.mark.parametrize("min_price", [99.99, 100, 100.01, None])
async def test_get_items__min_price(steam, csmoney, provider, min_price):
    steam.get_all.return_value = {"AK": (75, None)}
    csmoney.get_all.return_value = {"AK": 100}

    items = await provider.get_items(-100, min_price)

    should = 100 >= min_price if min_price else True
    assert len(items) == should

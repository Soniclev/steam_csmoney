import typing
from unittest import mock
from unittest.mock import AsyncMock, Mock

import pytest

from price_monitoring.models.steam import SkinSellHistory
from price_monitoring.telegram.offer_provider.redis_sell_history_provider import (
    RedisSellHistoryProvider,
    _MIN_SOLD_PER_WEEK,
    _get_percentile,
)

_MAX_THRESHOLD = -100


@pytest.fixture
def steam():
    return AsyncMock()


@pytest.fixture
def csmoney():
    obj = AsyncMock()
    obj.get_all.return_value = {"AK": 100}
    yield obj


@pytest.fixture
def provider(steam, csmoney):
    return RedisSellHistoryProvider(steam, csmoney)


def _create_history(
    is_stable: bool = True,
    sold_per_week: int = 10000,
    percentile_price: typing.Optional[float] = 75,
):
    summary = Mock(spec=SkinSellHistory)
    summary.market_name = "AK"
    summary.is_stable = is_stable
    summary.sold_per_week = sold_per_week
    summary.summary = {}
    summary.get = Mock(return_value=percentile_price)
    return summary


@pytest.mark.parametrize("is_stable", [True, False])
@pytest.mark.parametrize("sold_per_week", [0, 5, 50, 100, 1000, 10000])
@pytest.mark.parametrize("steam_price", [75, None])
@pytest.mark.parametrize("csmoney_item", [{"AK": 125}, {}])
async def test_get_items__existence(
    steam, csmoney, provider, is_stable, sold_per_week, csmoney_item, steam_price
):
    history = _create_history(
        is_stable=is_stable, sold_per_week=sold_per_week, percentile_price=steam_price
    )
    steam.get_all.return_value = {"AK": history}
    csmoney.get_all.return_value = csmoney_item

    items = await provider.get_items(_MAX_THRESHOLD)
    should = True
    if not is_stable:
        should = False
    if is_stable and history.sold_per_week < _MIN_SOLD_PER_WEEK:
        should = False
    if not csmoney_item or not steam_price:
        should = False

    assert len(items) == should


@pytest.mark.parametrize("percentage_limit", [5, 0, -24, -25, -26, None])
async def test_get_items__percentage_limit(steam, csmoney, provider, percentage_limit):
    history = _create_history()
    steam.get_all.return_value = {"AK": history}

    with mock.patch(
        "price_monitoring.telegram.offers.SteamSellHistoryOffer.compute_percentage"
    ) as m:
        m.return_value = -25
        items = await provider.get_items(percentage_limit)

    should = -25 >= percentage_limit if percentage_limit else True
    assert len(items) == should


@pytest.mark.parametrize("min_price", [99.99, 100, 100.01, None])
async def test_get_items__min_price(steam, csmoney, provider, min_price):
    history = _create_history()
    steam.get_all.return_value = {"AK": history}

    items = await provider.get_items(_MAX_THRESHOLD, min_price)

    should = 100 >= min_price if min_price else True
    assert len(items) == should


@pytest.mark.parametrize("price", [99.99, 100, 100.01, None])
async def test_get_items__percentile_adjusted(steam, csmoney, provider, price):
    history = _create_history()
    steam.get_all.return_value = {"AK": history}
    csmoney.get_all.return_value = {"AK": price} if price else {}

    await provider.get_items(_MAX_THRESHOLD)

    if price:
        expected = 50 if price < 100 else 20
        history.get.assert_called_with(expected)  # type: ignore
    else:
        history.get.assert_not_called()  # type: ignore


@pytest.mark.parametrize(
    "price, expected",
    [
        (99.99, 50),
        (100, 20),
        (100.01, 20),
    ],
)
def test_get_percentile(price, expected):
    assert _get_percentile(price) == expected

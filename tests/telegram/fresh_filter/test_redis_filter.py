import pytest

from price_monitoring.telegram.fresh_filter.redis_filter import RedisFilter
from price_monitoring.telegram.offers import BaseItemOffer

_offers = [
    BaseItemOffer(market_name="AK", orig_price=1, sell_price=2),
    BaseItemOffer(market_name="AK2", orig_price=2, sell_price=3),
    BaseItemOffer(market_name="AK3", orig_price=2, sell_price=3),
    BaseItemOffer(market_name="AK4", orig_price=2, sell_price=3),
]


@pytest.fixture()
def filter_(fake_redis):
    return RedisFilter(fake_redis)


@pytest.mark.parametrize(
    "loaded, passed, expected",
    [
        ([], _offers, _offers),
        (_offers[:1], _offers, _offers[1:]),
        (_offers[:2], _offers, _offers[2:]),
        (_offers[:3], _offers, _offers[3:]),
    ],
)
async def test_filter(filter_, loaded, passed, expected):
    await filter_.append_offers(loaded)

    new_offers = await filter_.filter_new_offers(_offers)

    assert new_offers == expected

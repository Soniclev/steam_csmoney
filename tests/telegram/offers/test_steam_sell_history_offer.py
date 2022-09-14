import pytest

from price_monitoring.telegram.offers import SteamSellHistoryOffer


@pytest.fixture()
def offer():
    return SteamSellHistoryOffer(
        market_name="AK",
        orig_price=1,
        suggested_price=1.2,
        mean_price=1.21,
        sold_per_week=100,
    )


@pytest.mark.parametrize("lock_status", ["TRADEBAN", None])
def test_create_notification(offer, lock_status):
    offer.lock_status = lock_status
    notification = offer.create_notification()

    if lock_status:
        assert notification.short_title == "AVG $1.21 | 100 SOLD IN WEEK | TRADEBAN"
    else:
        assert notification.short_title == "AVG $1.21 | 100 SOLD IN WEEK"
    assert notification.market_name == "AK"
    assert notification.orig_price == 1
    assert notification.sell_price == 1.2

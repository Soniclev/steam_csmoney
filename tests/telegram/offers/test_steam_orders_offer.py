import pytest

from price_monitoring.telegram.offers import SteamOrdersOffer


@pytest.fixture()
def offer():
    return SteamOrdersOffer(market_name="AK", orig_price=1, buy_order=1.2)


def test_create_notification(offer):
    notification = offer.create_notification()

    assert notification.short_title == "AUTOBUY"
    assert notification.market_name == "AK"
    assert notification.orig_price == 1
    assert notification.sell_price == 1.2

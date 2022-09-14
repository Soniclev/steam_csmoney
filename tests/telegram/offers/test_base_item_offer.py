import pytest

from price_monitoring.telegram.offers.base_item_offer import BaseItemOffer


@pytest.mark.parametrize(
    "offer, diff",
    [
        (BaseItemOffer("", 10, 10), 0),
        (BaseItemOffer("", 10, 9), -1),
        (BaseItemOffer("", 10, 11.5), 1.5),
        (BaseItemOffer("", 10.01, 10.02), 0.01),
    ],
)
def test_compute_difference(offer, diff):
    assert offer.compute_difference() == diff


@pytest.mark.parametrize(
    "offer, percentage",
    [
        (BaseItemOffer("", 10, 10), 0),
        (BaseItemOffer("", 10, 9), -10),
        (BaseItemOffer("", 10, 11.5), 15),
        (BaseItemOffer("", 10, 10.1), 1),
        (BaseItemOffer("", 10, 10.01), 0.1),
    ],
)
def test_compute_percentage(offer, percentage):
    assert offer.compute_percentage() == percentage


def test_create_notification():
    offer = BaseItemOffer("AK", 10, 11.5)

    notification = offer.create_notification()

    assert notification.market_name == offer.market_name
    assert notification.orig_price == offer.orig_price
    assert notification.sell_price == offer.sell_price
    assert notification.short_title == "UNKNOWN"

import pytest

from price_monitoring.telegram.models import ItemOfferNotification


@pytest.fixture()
def notification():
    return ItemOfferNotification(
        market_name="StatTrak™ M249 | Aztec (Field-Tested)",
        orig_price=0.25,
        sell_price=0.21,
        short_title="AUTOBUY",
    )


def test_compute_percentage_diff(notification):
    diff = notification.compute_percentage_diff()

    assert diff == -16

from unittest import mock

import pytest

from price_monitoring.telegram.bot.notification_formatter import to_markdown, several_to_markdown
from price_monitoring.telegram.models import ItemOfferNotification


@pytest.fixture()
def notification():
    return ItemOfferNotification(
        market_name="StatTrak™ M249 | Aztec (Field-Tested)",
        orig_price=0.25,
        sell_price=0.21,
        short_title="AUTOBUY",
    )


@pytest.fixture(autouse=True, scope="function")
def mock_add_fee():
    with mock.patch("price_monitoring.telegram.steam_fee.SteamFee.add_fee") as add_fee:
        add_fee.return_value = 0.27
        yield add_fee


def test_to_markdown(notification):
    text = to_markdown(notification)

    assert (
        text
        == """*\\-16\\.0%*  $0\\.25 \\-\\> $0\\.21 \\($0\\.27\\)  _\rAUTOBUY_\r
`StatTrak™ M249 \\| Aztec \\(Field\\-Tested\\)`
[StatTrak™ M249 \\| Aztec \\(Field\\-Tested\\)](https://steamcommunity\\.com/market/listings/730/StatTrak™ M249 \\| Aztec \\(Field\\-Tested\\))"""
    )


def test_several_to_markdown(notification):
    with mock.patch("price_monitoring.telegram.bot.notification_formatter.to_markdown") as func:
        func.return_value = "123"
        result = several_to_markdown([notification for _ in range(3)])

    assert result == "\n\n".join(["123"] * 3)

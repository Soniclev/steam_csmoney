from unittest.mock import AsyncMock

import pytest
from aiogram.types import ParseMode

from price_monitoring.telegram.bot.commands.offers import Offers
from price_monitoring.telegram.bot.notification_formatter import several_to_markdown, to_markdown
from price_monitoring.telegram.models import ItemOfferNotification
from price_monitoring.telegram.offers import BaseItemOffer


@pytest.fixture()
def offer_provider():
    return AsyncMock()


@pytest.fixture()
def command(offer_provider):
    return Offers(offer_provider)


async def test__offer_provider_call(offer_provider, command, message):
    offer_provider.get_items.return_value = []

    await command.handler(message)

    offer_provider.get_items.assert_awaited()


async def test__no_offers(offer_provider, command, message):
    offer_provider.get_items.return_value = []

    await command.handler(message)

    message.reply.assert_awaited_with(
        "Текущие предложения:\n",
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
    )


async def test__offers_sorted(offer_provider, command, message):
    offer_provider.get_items.return_value = [
        BaseItemOffer("M4A1", 10, 8),
        BaseItemOffer("AK", 10, 9),  # this one is more profitable than first one
    ]

    await command.handler(message)

    # offers sorted from high profitable to low
    s = "Текущие предложения:\n"
    s += several_to_markdown(
        [
            ItemOfferNotification(
                market_name="AK", orig_price=10, sell_price=9, short_title="UNKNOWN"
            ),
            ItemOfferNotification(
                market_name="M4A1", orig_price=10, sell_price=8, short_title="UNKNOWN"
            ),
        ]
    )
    message.reply.assert_awaited_with(
        s, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
    )


async def test__message_split(offer_provider, command, message):
    offer_provider.get_items.return_value = [BaseItemOffer("AK", 10, i) for i in range(1, 100)]

    await command.handler(message)

    assert message.reply.call_count > 1
    parts = [x[0][0] for x in message.reply.call_args_list]
    for i in range(1, 100):
        notification = ItemOfferNotification(
            market_name="AK", orig_price=10, sell_price=i, short_title="UNKNOWN"
        )
        text = to_markdown(notification)
        assert any(text in x for x in parts)


async def test__reply_with_error(offer_provider, command, message):
    offer_provider.get_items.side_effect = ValueError("There is an error!")

    await command.handler(message)

    message.reply.assert_awaited_with("There is an error!")

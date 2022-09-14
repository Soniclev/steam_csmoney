from unittest.mock import AsyncMock

import pytest

from price_monitoring.telegram.offers import BaseItemOffer
from price_monitoring.telegram.runner.runner_impl import Runner


@pytest.fixture()
def bot():
    return AsyncMock()


@pytest.fixture()
def price_provider():
    return AsyncMock()


@pytest.fixture()
def filter_():
    return AsyncMock()


@pytest.fixture()
def runner(bot, price_provider, filter_, disable_asyncio_sleep):
    return Runner(bot=bot, price_provider=price_provider, filter_=filter_)


async def test_filter_called(runner, price_provider, filter_):
    offers = [BaseItemOffer("AK", 10, 9)]
    price_provider.get_items.return_value = offers

    await runner.run()

    filter_.filter_new_offers.assert_called_with(offers)


async def test_filter_applied_to_offers(runner, price_provider, filter_):
    offers = [BaseItemOffer("AK", 10, 9)]
    price_provider.get_items.return_value = offers
    filter_.filter_new_offers.return_value = []

    await runner.run()

    filter_.append_offers.assert_called_with(offers)


async def test_new_offers_sent(runner, price_provider, bot, filter_):
    offer1 = BaseItemOffer("AK", 10, 9)
    offer2 = BaseItemOffer("M4A1", 11, 12)
    price_provider.get_items.return_value = [offer1, offer2]
    filter_.filter_new_offers.return_value = [offer1]

    await runner.run()

    bot.notify.assert_called_once_with(offer1.create_notification())

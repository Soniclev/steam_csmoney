from unittest.mock import AsyncMock

import pytest

from price_monitoring.models.steam import SteamSkinHistogram
from price_monitoring.worker.processing.steam_skin_processor import (
    _extract_buy_order,
    _extract_sell_order,
    SteamSkinProcessor,
)


def response():
    return {"highest_buy_order": "12", "lowest_sell_order": "14"}


def response_without_sell():
    return {"highest_buy_order": "12", "lowest_sell_order": None}


def response_without_buy():
    return {"highest_buy_order": None, "lowest_sell_order": "3"}


def empty_response():
    return {}


@pytest.mark.parametrize(
    "data, price",
    [
        (response, 0.12),
        (response_without_sell, 0.12),
        (response_without_buy, None),
        (empty_response, None),
    ],
)
def test_extract_buy_order(data, price):
    assert _extract_buy_order(data()) == price


@pytest.mark.parametrize(
    "data, price",
    [
        (response, 0.14),
        (response_without_sell, None),
        (response_without_buy, 0.03),
        (empty_response, None),
    ],
)
def test_extract_sell_order(data, price):
    assert _extract_sell_order(data()) == price


@pytest.fixture()
def steam_order_storage():
    return AsyncMock()


@pytest.fixture()
def processor(steam_order_storage):
    return SteamSkinProcessor(steam_order_storage)


def skin_factory(buy: int, sell: int):
    return SteamSkinHistogram(
        market_name="AK", response={"highest_buy_order": buy, "lowest_sell_order": sell}
    )


@pytest.mark.parametrize(
    "buy,sell",
    [
        (15, 17),
        (None, 17),
        (15, None),
        (None, None),
    ],
)
async def test_process(processor, steam_order_storage, buy, sell):
    skin = skin_factory(buy, sell)

    await processor.process(skin)

    # divide by 100 to convert cents to dollars
    buy_excepted = buy / 100 if buy else None
    sell_excepted = sell / 100 if sell else None
    steam_order_storage.update_skin_order.assert_called_with(
        market_name="AK", buy_order=buy_excepted, sell_order=sell_excepted
    )

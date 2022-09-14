from unittest.mock import AsyncMock

import pytest

from price_monitoring.models.steam import SteamSellHistory
from price_monitoring.queues.rabbitmq.steam_sell_history_queue import (
    SteamSellHistoryReader,
    SteamSellHistoryWriter,
)


def _create_history():
    return SteamSellHistory(market_name="AK", encoded_data="[]")


@pytest.fixture()
def reader():
    return AsyncMock()


@pytest.fixture()
def queue_reader(reader):
    return SteamSellHistoryReader(reader)


@pytest.fixture()
def publisher():
    return AsyncMock()


@pytest.fixture()
def queue_writer(publisher):
    return SteamSellHistoryWriter(publisher)


@pytest.mark.parametrize(
    "data, skin",
    [
        (_create_history().dump_bytes(), _create_history()),
        (None, None),
    ],
)
async def test_get(queue_reader, reader, data, skin):
    reader.read.return_value = data

    result = await queue_reader.get(timeout=1)

    assert result == skin
    reader.read.assert_called_with(timeout=1)


async def test_put(queue_writer, publisher):
    skin = _create_history()
    await queue_writer.put(skin)

    publisher.publish.assert_called_with(skin.dump_bytes())

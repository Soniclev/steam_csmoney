from unittest.mock import AsyncMock

import pytest

from price_monitoring.models.steam import MarketNamePack
from price_monitoring.queues.rabbitmq.market_name_queue import MarketNameReader, MarketNameWriter

_PACK = MarketNamePack(items=["AK", "M4A1"])


@pytest.fixture()
def reader():
    return AsyncMock()


@pytest.fixture()
def queue_reader(reader):
    return MarketNameReader(reader)


@pytest.fixture()
def publisher():
    return AsyncMock()


@pytest.fixture()
def queue_writer(publisher):
    return MarketNameWriter(publisher)


@pytest.mark.parametrize(
    "data, items",
    [
        (_PACK.dump_bytes(), _PACK),
        (None, None),
    ],
)
async def test_get(queue_reader, reader, data, items):
    reader.read.return_value = data

    result = await queue_reader.get(timeout=1)

    assert result == items
    reader.read.assert_called_with(timeout=1)


async def test_put(queue_writer, publisher):
    await queue_writer.put(_PACK)

    publisher.publish.assert_called_with(_PACK.dump_bytes())

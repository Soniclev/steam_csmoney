from unittest.mock import AsyncMock

import pytest

from price_monitoring.models.csmoney import CsmoneyItemPack
from price_monitoring.queues.rabbitmq.csmoney_result_queue import CsmoneyWriter, CsmoneyReader


def _create_item_pack():
    return CsmoneyItemPack(items=[])


@pytest.fixture()
def reader():
    return AsyncMock()


@pytest.fixture()
def queue_reader(reader):
    return CsmoneyReader(reader)


@pytest.fixture()
def publisher():
    return AsyncMock()


@pytest.fixture()
def queue_writer(publisher):
    return CsmoneyWriter(publisher)


@pytest.mark.parametrize(
    "data, item_pack",
    [
        (_create_item_pack().dump_bytes(), _create_item_pack()),
        (None, None),
    ],
)
async def test_get(queue_reader, reader, data, item_pack):
    reader.read.return_value = data

    result = await queue_reader.get(timeout=1)

    assert result == item_pack
    reader.read.assert_called_with(timeout=1)


async def test_put(queue_writer, publisher):
    item_pack = _create_item_pack()
    await queue_writer.put(item_pack)

    publisher.publish.assert_called_with(item_pack.dump_bytes())

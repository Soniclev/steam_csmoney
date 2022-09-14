from unittest.mock import AsyncMock

import pytest

from price_monitoring.models.steam import SteamSkinHistogram
from price_monitoring.queues.rabbitmq.steam_result_queue import SteamOrderWriter, SteamOrderReader


def _create_skin():
    return SteamSkinHistogram(market_name="AK", response=dict(foo="bar"))


@pytest.fixture()
def reader():
    return AsyncMock()


@pytest.fixture()
def queue_reader(reader):
    return SteamOrderReader(reader)


@pytest.fixture()
def publisher():
    return AsyncMock()


@pytest.fixture()
def queue_writer(publisher):
    return SteamOrderWriter(publisher)


@pytest.mark.parametrize(
    "data, skin",
    [
        (_create_skin().dump_bytes(), _create_skin()),
        (None, None),
    ],
)
async def test_get(queue_reader, reader, data, skin):
    reader.read.return_value = data

    result = await queue_reader.get(timeout=1)

    assert result == skin
    reader.read.assert_called_with(timeout=1)


async def test_put(queue_writer, publisher):
    skin = _create_skin()
    await queue_writer.put(skin)

    publisher.publish.assert_called_with(skin.dump_bytes())

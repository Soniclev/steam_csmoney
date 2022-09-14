import datetime
from unittest.mock import AsyncMock

import pytest

from price_monitoring.models.csmoney import CsmoneyItem, CsmoneyItemPack, CsmoneyItemCategory
from price_monitoring.worker.processing.csmoney_item_processor import CsmoneyItemProcessor

_item1 = CsmoneyItem(
    name="AK",
    price=0.5,
    unlock_timestamp=None,
    type_=CsmoneyItemCategory.RIFLE,
    asset_id="1",
    name_id=1,
)
_item2 = CsmoneyItem(
    name="M4A1",
    price=0.5,
    unlock_timestamp=datetime.datetime(2022, 5, 25, 10, 0, 0),
    type_=CsmoneyItemCategory.RIFLE,
    asset_id="3",
    name_id=2,
)


@pytest.fixture()
def unlocked_item_storage():
    return AsyncMock()


@pytest.fixture()
def locked_item_storage():
    return AsyncMock()


@pytest.fixture()
def processor(unlocked_item_storage, locked_item_storage):
    return CsmoneyItemProcessor(
        unlocked_storage=unlocked_item_storage, locked_storage=locked_item_storage
    )


_TEST_DATA = [
    (_item1, False),
    (_item2, True),
]


@pytest.mark.parametrize("item, is_locked", _TEST_DATA)
async def test_process(processor, unlocked_item_storage, locked_item_storage, item, is_locked):
    pack = CsmoneyItemPack(items=[item])

    await processor.process(pack)

    storage = locked_item_storage if is_locked else unlocked_item_storage
    unused_storage = locked_item_storage if not is_locked else unlocked_item_storage
    storage.update_item.assert_awaited_once_with(item.name, item.price)
    unused_storage.update_item.assert_not_called()

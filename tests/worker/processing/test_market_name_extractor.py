from unittest.mock import AsyncMock

import pytest

from price_monitoring.models.csmoney import CsmoneyItem, CsmoneyItemPack, CsmoneyItemCategory
from price_monitoring.worker.processing.market_name_extractor import MarketNameExtractor

_item1 = CsmoneyItem(
    name="AK",
    price=0.5,
    unlock_timestamp=None,
    type_=CsmoneyItemCategory.RIFLE,
    asset_id="1",
    name_id=1,
)
_item2 = CsmoneyItem(
    name="AK",
    price=0.5,
    unlock_timestamp=None,
    type_=CsmoneyItemCategory.RIFLE,
    asset_id="2",
    name_id=1,
)
_item3 = CsmoneyItem(
    name="M4A1",
    price=0.5,
    unlock_timestamp=None,
    type_=CsmoneyItemCategory.RIFLE,
    asset_id="3",
    name_id=2,
)


@pytest.fixture()
def market_name_queue():
    return AsyncMock()


@pytest.fixture()
def processor(market_name_queue):
    return MarketNameExtractor(market_name_queue=market_name_queue)


_TEST_DATA = [
    ([_item1, _item2, _item3], ("AK", "M4A1")),
    ([_item1, _item3], ("AK", "M4A1")),
    ([_item1, _item2], ("AK",)),
    ([_item3], ("M4A1",)),
]


@pytest.mark.parametrize("items, market_names", _TEST_DATA)
async def test_process(processor, market_name_queue, market_names, items):
    pack = CsmoneyItemPack(items=items)

    await processor.process(pack)

    market_name_queue.put.assert_awaited_once()
    pack = market_name_queue.put.call_args[0][0]
    assert sorted(pack.items) == sorted(market_names)

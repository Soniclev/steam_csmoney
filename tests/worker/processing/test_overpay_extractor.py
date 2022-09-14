from unittest.mock import AsyncMock

import pytest

from price_monitoring.features.overpay.worker.overpay_extractor import OverpayExtractor
from price_monitoring.models.csmoney import (
    CsmoneyItem,
    CsmoneyItemPack,
    CsmoneyItemOverpay,
    CsmoneyItemCategory,
)


@pytest.fixture()
def overpay_storage():
    return AsyncMock()


@pytest.fixture()
def processor(overpay_storage):
    return OverpayExtractor(overpay_storage=overpay_storage)


_TEST_DATA = [
    (
        CsmoneyItem(
            name="AK",
            price=0.5,
            asset_id="1",
            float_="0.0123",
            type_=CsmoneyItemCategory.RIFLE,
            overpay_float=0.1,
            name_id=1,
        ),
        CsmoneyItemOverpay(market_name="AK", float_="0.0123", name_id=1, overpay=0.1),
    ),
    (
        CsmoneyItem(
            name="AK",
            price=0.5,
            asset_id="1",
            float_="0.0123",
            type_=CsmoneyItemCategory.RIFLE,
            overpay_float=None,
            name_id=1,
        ),
        None,
    ),
]


@pytest.mark.parametrize("item, item_overpay", _TEST_DATA)
async def test_process(processor, overpay_storage, item, item_overpay):
    pack = CsmoneyItemPack(items=[item])

    await processor.process(pack)

    if item_overpay:
        overpay_storage.add_overpay.assert_awaited_with(item_overpay)
    else:
        overpay_storage.add_overpay.assert_not_called()

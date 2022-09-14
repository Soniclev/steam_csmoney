import typing
from unittest.mock import AsyncMock, patch

import pytest

from price_monitoring.features.overpay.base_price_filler import fill_base_price_storage, _grouper
from price_monitoring.features.overpay.storage import RedisBasePriceStorage
from price_monitoring.models.csmoney import CsmoneyItemOverpay


@pytest.fixture()
def storage(fake_redis):
    return RedisBasePriceStorage(fake_redis)


@pytest.fixture()
def fetcher():
    return AsyncMock()


TEST_DATA = [
    ([1, 2, 3, 4, 5], 1, [[1], [2], [3], [4], [5]]),
    ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
    ([1, 2, 3, 4, 5], 3, [[1, 2, 3], [4, 5]]),
    ([1, 2, 3, 4, 5], 4, [[1, 2, 3, 4], [5]]),
    ([1, 2, 3, 4, 5], 5, [[1, 2, 3, 4, 5]]),
    ([1, 2, 3, 4, 5], 6, [[1, 2, 3, 4, 5]]),
]


@pytest.mark.parametrize("iterable, n, expected", TEST_DATA)
def test_grouper(iterable, n, expected):
    assert _grouper(iterable, n) == expected


async def test_fill_base_price_storage__not_called(storage, fetcher):
    await fill_base_price_storage([], storage, fetcher)

    assert await storage.get_all() == {}
    fetcher.get.assert_not_called()


async def test_fill_base_price_storage(storage, fetcher):
    item_overpay = CsmoneyItemOverpay(market_name="AK", name_id=1, float_="0.123", overpay=0.21)
    fetcher.get.return_value = {1: 12.3}

    await fill_base_price_storage([item_overpay], storage, fetcher)

    assert await storage.get_all() == {"AK": 12.3}


async def test_fill_base_price_storage_several(storage, fetcher):
    async def _get(name_ids: typing.List[int]) -> typing.Dict[int, float]:
        return {name_id: float(name_id) + 0.05 for name_id in name_ids}

    fetcher.get = _get
    items = [
        CsmoneyItemOverpay(market_name=f"AK_{i}", name_id=i, float_="0.123", overpay=0.21)
        for i in range(1, 5)
    ]

    await fill_base_price_storage(items, storage, fetcher)

    assert await storage.get_all() == {
        "AK_1": 1.05,
        "AK_2": 2.05,
        "AK_3": 3.05,
        "AK_4": 4.05,
    }


async def test_fill_base_price_storage_handle_duplicates(storage, fetcher):
    items = [
        CsmoneyItemOverpay(market_name=f"AK_1", name_id=1, float_="0.123", overpay=0.21)
        for _ in range(100)
    ]

    with patch.object(fetcher, "get", return_value={1: 1.05}) as wrapped:
        await fill_base_price_storage(items, storage, fetcher)
        wrapped.assert_called_once_with([1])

    assert await storage.get_all() == {"AK_1": 1.05}


async def test_fill_base_price_storage_not_fail(storage, fetcher):
    items = [
        CsmoneyItemOverpay(market_name=f"AK_1", name_id=1, float_="0.123", overpay=0.21)
        for _ in range(100)
    ]

    with patch.object(fetcher, "get", side_effect=ValueError("There was an error!")) as wrapped:
        await fill_base_price_storage(items, storage, fetcher)
        wrapped.assert_called_once_with([1])

    assert await storage.get_all() == {}

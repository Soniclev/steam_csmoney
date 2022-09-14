import asyncio
import logging
from typing import Iterable

from .csmoney import AbstractBasePriceFetcher
from .storage import AbstractBasePriceStorage
from ...models.csmoney import CsmoneyItemOverpay

GROUP_SIZE = 10  # wiki.cs.money endpoint allows to request several name_ids once

logger = logging.getLogger(__name__)


def _grouper(iterable: Iterable, size: int):
    assert size > 0
    result = []
    subarray = []
    for i, obj in enumerate(iterable, start=1):
        subarray.append(obj)
        if i % size == 0:
            result.append(subarray)
            subarray = []
    if subarray:
        result.append(subarray)
    return result


async def fill_base_price_storage(
    overpays: list[CsmoneyItemOverpay],
    base_price_storage: AbstractBasePriceStorage,
    base_price_fetcher: AbstractBasePriceFetcher,
):
    existed_market_names = (await base_price_storage.get_all()).keys()
    new_name_ids = {
        overpay.name_id: overpay.market_name
        for overpay in overpays
        if overpay.market_name not in existed_market_names
    }

    tasks = []
    for group in _grouper(new_name_ids, GROUP_SIZE):
        try:
            base_prices = await base_price_fetcher.get(group)
        except ValueError:
            logger.warning(f"Failed to get base prices for {group}")
            continue
        for name_id, base_price in base_prices.items():
            market_name = new_name_ids[name_id]
            tasks.append(
                asyncio.create_task(base_price_storage.update_item(market_name, base_price))
            )

    await asyncio.gather(*tasks)

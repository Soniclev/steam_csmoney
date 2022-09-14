import asyncio
import logging

from .abstract_csmoney_item_processor import AbstractCsmoneyItemProcessor
from ...models.csmoney import CsmoneyItemPack
from ...storage.csmoney import AbstractCsmoneyItemStorage

logger = logging.getLogger(__name__)


class CsmoneyItemProcessor(AbstractCsmoneyItemProcessor):
    def __init__(
        self,
        unlocked_storage: AbstractCsmoneyItemStorage,
        locked_storage: AbstractCsmoneyItemStorage,
    ):
        self._unlocked_storage = unlocked_storage
        self._locked_storage = locked_storage

    async def process(self, pack: CsmoneyItemPack) -> None:
        await asyncio.gather(
            *[
                self._locked_storage.update_item(item.name, item.price)
                if item.unlock_timestamp
                else self._unlocked_storage.update_item(item.name, item.price)
                for item in pack.items
            ]
        )
        logger.info(f"Updated {len(pack.items)} cs.money items")

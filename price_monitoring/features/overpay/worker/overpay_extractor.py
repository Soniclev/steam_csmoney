import asyncio
import logging

from ..storage import AbstractOverpayStorage
from ....models.csmoney import CsmoneyItemPack, CsmoneyItemOverpay, CsmoneyItemCategory
from ....worker.processing import AbstractCsmoneyItemProcessor


_IGNORE_CATEGORIES = {CsmoneyItemCategory.KNIFE, CsmoneyItemCategory.GLOVE}
logger = logging.getLogger(__name__)


class OverpayExtractor(AbstractCsmoneyItemProcessor):
    def __init__(self, overpay_storage: AbstractOverpayStorage):
        self._overpay_storage = overpay_storage

    async def process(self, pack: CsmoneyItemPack) -> None:
        await asyncio.gather(
            *[
                self._overpay_storage.add_overpay(
                    CsmoneyItemOverpay(
                        market_name=item.name,
                        float_=item.float_,
                        name_id=item.name_id,
                        overpay=item.overpay_float,
                    )
                )
                for item in pack.items
                if item.overpay_float and item.float_
                if item.type_ not in _IGNORE_CATEGORIES
            ]
        )
        logger.info(f"Checked {len(pack.items)} cs.money items for overpay")

import logging

from .abstract_csmoney_item_processor import AbstractCsmoneyItemProcessor
from ...models.csmoney import CsmoneyItemPack
from ...models.steam import MarketNamePack
from ...queues import AbstractMarketNameWriter

logger = logging.getLogger(__name__)


class MarketNameExtractor(AbstractCsmoneyItemProcessor):
    def __init__(self, market_name_queue: AbstractMarketNameWriter):
        self._market_name_queue = market_name_queue

    async def process(self, pack: CsmoneyItemPack) -> None:
        market_names = {item.name for item in pack.items}
        market_name_pack = MarketNamePack(items=list(market_names))
        await self._market_name_queue.put(market_name_pack)
        logger.info(f"Updated market names for items {market_names}")

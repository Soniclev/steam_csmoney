import asyncio
import logging

from common.tracer import trace, annotate
from .abstract_runner import AbstractRunner
from ..bot import AbstractBot
from ..fresh_filter import AbstractFilter
from ..offer_provider import AbstractOfferProvider
from ...decorators import async_infinite_loop

logger = logging.getLogger(__name__)


class Runner(AbstractRunner):
    def __init__(
        self,
        bot: AbstractBot,
        price_provider: AbstractOfferProvider,
        filter_: AbstractFilter,
    ):
        self.bot = bot
        self.price_provider = price_provider
        self.filter_ = filter_

    @async_infinite_loop(logger)
    @trace
    async def run(self) -> None:
        offers = await self.price_provider.get_items()
        annotate(f"Got {len(offers)} offers from {len(offers)}")
        new_offers = await self.filter_.filter_new_offers(offers)
        annotate(f"Filtered out {len(offers) - len(new_offers)}")
        logger.info(f"Got {len(new_offers)} new offers from {len(offers)}")
        annotate(f"Got {len(new_offers)} new offers from {len(offers)}")
        await self.filter_.append_offers(offers)

        for offer in new_offers:
            notification = offer.create_notification()
            asyncio.create_task(self.bot.notify(notification))

        await asyncio.sleep(10)

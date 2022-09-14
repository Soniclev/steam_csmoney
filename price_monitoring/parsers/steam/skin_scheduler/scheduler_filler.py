import asyncio
import logging
from typing import Iterable

from .abstract_skin_scheduler import AbstractSkinScheduler
from ....decorators import async_infinite_loop
from ....queues import AbstractMarketNameReader

logger = logging.getLogger(__name__)


class SchedulerFiller:
    def __init__(
        self,
        market_name_queue: AbstractMarketNameReader,
        skin_schedulers: Iterable[AbstractSkinScheduler],
    ):
        self._market_name_queue = market_name_queue
        self._skin_schedulers = skin_schedulers

    async def run(self) -> None:
        await self._run_market_name_reader()

    @async_infinite_loop(logger)
    async def _run_market_name_reader(self) -> None:
        pack = await self._market_name_queue.get(timeout=10)
        if not pack:
            await asyncio.sleep(0.5)
            return

        await asyncio.gather(
            *[
                scheduler.append_market_name(market_name)
                for market_name in pack.items
                for scheduler in self._skin_schedulers
            ]
        )

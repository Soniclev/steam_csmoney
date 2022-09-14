import asyncio
import logging

from .parser import AbstractSellHistoryParser
from .skin_scheduler import AbstractSkinScheduler
from ..abstract_parser import AbstractParser
from ...decorators import async_infinite_loop
from ...queues import AbstractSteamSellHistoryWriter

logger = logging.getLogger(__name__)


class SteamSellHistoryParser(AbstractParser):
    def __init__(
        self,
        parser: AbstractSellHistoryParser,
        skin_scheduler: AbstractSkinScheduler,
        result_queue: AbstractSteamSellHistoryWriter,
    ):
        self._parser = parser
        self._skin_scheduler = skin_scheduler
        self._result_queue = result_queue

    async def run(self) -> None:
        await self._run_steam_parser()

    @async_infinite_loop(logger)
    async def _run_steam_parser(self) -> None:
        market_name = await self._skin_scheduler.get_skin()
        if not market_name:
            await asyncio.sleep(0.5)
            return

        is_success = False
        try:
            is_success = await self._parser.fetch_history(
                market_name=market_name, result_queue=self._result_queue
            )
        except Exception as exc:
            logger.exception(exc)
        await self._skin_scheduler.release_skin(market_name, is_success)

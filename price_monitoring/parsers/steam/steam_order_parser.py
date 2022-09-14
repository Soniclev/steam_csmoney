import asyncio
import logging

from .parser import AbstractSteamOrdersParser
from .skin_scheduler import AbstractSkinScheduler
from ..abstract_parser import AbstractParser
from ...decorators import async_infinite_loop
from ...queues import AbstractSteamOrderWriter

logger = logging.getLogger(__name__)


class SteamOrderParser(AbstractParser):
    def __init__(
        self,
        parser: AbstractSteamOrdersParser,
        skin_scheduler: AbstractSkinScheduler,
        steam_result_queue: AbstractSteamOrderWriter,
    ):
        self._parser = parser
        self._skin_scheduler = skin_scheduler
        self._steam_result_queue = steam_result_queue

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
            is_success = await self._parser.fetch_orders(
                market_name=market_name, result_queue=self._steam_result_queue
            )
        except Exception as exc:
            logger.exception(exc)
        await self._skin_scheduler.release_skin(market_name, is_success)

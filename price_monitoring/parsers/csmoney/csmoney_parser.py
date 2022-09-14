import asyncio
import logging

from .parser import AbstractCsmoneyParser
from .task_scheduler import RedisTaskScheduler
from ..abstract_parser import AbstractParser
from ...decorators import async_infinite_loop
from ...queues import AbstractCsmoneyWriter

logger = logging.getLogger(__name__)


class CsmoneyParser(AbstractParser):
    def __init__(
        self,
        impl: AbstractCsmoneyParser,
        result_queue: AbstractCsmoneyWriter,
        task_scheduler: RedisTaskScheduler,
    ):
        self._impl = impl
        self._result_queue = result_queue
        self._task_scheduler = task_scheduler

    @async_infinite_loop(logger)
    async def run(self) -> None:
        csm_task = await self._task_scheduler.get_task()
        if not csm_task:
            await asyncio.sleep(5)
            return

        try:
            logger.info("Start to work with a task")
            task = asyncio.create_task(self._impl.parse(csm_task.url, self._result_queue))
            while not task.done():
                await self._task_scheduler.renew_task_lock(csm_task)
                logger.info("Lock for task successfully renewed")
                await asyncio.sleep(10)
            is_failed = task.cancelled() or (task.exception() is not None)
            if task.exception():
                logger.exception(
                    "Got an exception while parsing cs.money", exc_info=task.exception()
                )
            await self._task_scheduler.release_task(csm_task, not is_failed)
            logging.info(f"Lock for task successfully released as {is_failed=}")
        except Exception as exc:
            await self._task_scheduler.release_task(csm_task, False)
            logger.exception("Lock for task successfully released as failed", exc_info=exc)
            raise exc

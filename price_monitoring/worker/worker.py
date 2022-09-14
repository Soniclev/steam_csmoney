import asyncio
import logging
import typing
from dataclasses import dataclass

from ..decorators import async_infinite_loop

logger = logging.getLogger(__name__)


@dataclass
class WorkerThread:
    reader: typing.Any
    delay_duration: float
    processors: typing.Iterable[typing.Any]


@async_infinite_loop(logger)
async def _run_processor(thread: WorkerThread) -> None:
    item = await thread.reader.get()
    if not item:
        await asyncio.sleep(thread.delay_duration)
        return
    await asyncio.gather(*[processor.process(item) for processor in thread.processors])


class Worker:
    def __init__(self, threads: typing.Iterable[WorkerThread]):
        self._threads = threads

    async def run(self) -> None:
        await asyncio.gather(
            *[asyncio.create_task(_run_processor(thread)) for thread in self._threads]
        )

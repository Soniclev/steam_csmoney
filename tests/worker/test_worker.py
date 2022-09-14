from unittest.mock import AsyncMock

import pytest

from price_monitoring.worker.worker import Worker, WorkerThread


@pytest.fixture()
def processor():
    return AsyncMock()


@pytest.fixture()
def reader():
    return AsyncMock()


@pytest.fixture()
def worker(disable_asyncio_sleep, processor, reader):
    return Worker([WorkerThread(reader=reader, delay_duration=0.1, processors=[processor])])


@pytest.mark.parametrize("item", [None, 1])
async def test_run_steam_skin_processor(worker, reader, processor, item):
    reader.get.return_value = item

    await worker.run()

    if item:
        processor.process.assert_awaited_with(item)
    else:
        processor.process.assert_not_called()


async def test_run__do_not_crash(worker, reader):
    reader.get.side_effect = Exception()

    await worker.run()


if __name__ == "__main__":
    pytest.main()

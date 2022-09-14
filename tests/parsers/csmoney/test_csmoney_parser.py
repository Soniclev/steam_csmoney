from unittest.mock import AsyncMock

import pytest

from price_monitoring import decorators
from price_monitoring.models.csmoney import CsmoneyTask
from price_monitoring.parsers.csmoney.csmoney_parser import CsmoneyParser


@pytest.fixture()
def parser_impl():
    return AsyncMock()


@pytest.fixture()
def result_queue():
    return AsyncMock()


@pytest.fixture()
def task_scheduler():
    return AsyncMock()


@pytest.fixture()
def parser(parser_impl, result_queue, task_scheduler):
    decorators._INFINITE_RUN = False  # disable infinite loops
    return CsmoneyParser(parser_impl, result_queue, task_scheduler)


@pytest.mark.parametrize("task", [CsmoneyTask(url="1"), None])
async def test_run__task_started(
    disable_asyncio_sleep, parser, parser_impl, task_scheduler, result_queue, task
):
    task_scheduler.get_task.return_value = task

    await parser.run()

    if task:
        parser_impl.parse.assert_awaited_with(task.url, result_queue)
    else:
        parser_impl.parse.assert_not_awaited()


async def test_run__task_renewed(disable_asyncio_sleep, parser, task_scheduler):
    task = CsmoneyTask(url="1")
    task_scheduler.get_task.return_value = task

    await parser.run()

    task_scheduler.renew_task_lock.assert_awaited_with(task)


@pytest.mark.parametrize(
    "parser_exc, scheduler_exc, is_success",
    [
        (None, None, True),
        (Exception(), None, False),
        (None, Exception(), False),
    ],
)
async def test_run__task_released(
    disable_asyncio_sleep,
    parser,
    parser_impl,
    task_scheduler,
    parser_exc,
    scheduler_exc,
    is_success,
):
    task = CsmoneyTask(url="1")
    task_scheduler.get_task.return_value = task
    parser_impl.parse.side_effect = parser_exc
    task_scheduler.renew_task_lock.side_effect = scheduler_exc

    await parser.run()

    task_scheduler.release_task.assert_awaited_with(task, is_success)


if __name__ == "__main__":
    pytest.main()

import pytest
from freezegun import freeze_time

from price_monitoring.models.csmoney import CsmoneyTask
from price_monitoring.parsers.csmoney.task_scheduler.redis_task_scheduler import (
    RedisTaskScheduler,
    RenewFailedError,
)


@pytest.fixture()
def task():
    return CsmoneyTask(url="123")


@pytest.fixture()
def scheduler(fake_redis):
    return RedisTaskScheduler(fake_redis)


async def test_get_task__no_tasks(scheduler, task):
    assert not await scheduler.get_task()


async def test_get_task__append_task(scheduler, task):
    await scheduler.append_task(task)

    assert await scheduler.get_task() == task


async def test_get_task__task_is_not_available(scheduler, task):
    await scheduler.append_task(task)

    await scheduler.get_task()

    assert not await scheduler.get_task()


async def test_delete_task(scheduler, task):
    await scheduler.append_task(task)
    await scheduler.delete_task(task)

    assert not await scheduler.get_task()


@pytest.mark.parametrize("is_success", [True, False])
async def test_release_task(scheduler, task, is_success):
    await scheduler.append_task(task)
    assert await scheduler.get_task() == task

    await scheduler.release_task(task, is_success)

    if is_success:
        assert not await scheduler.get_task()
    else:
        assert await scheduler.get_task() == task


async def test_task_is_unlocked_after_time(scheduler, task):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_task(task)

    with freeze_time("2022-01-14 12:00:00"):
        assert await scheduler.get_task() == task

    with freeze_time("2022-01-14 12:00:01"):
        assert not await scheduler.get_task()
    with freeze_time("2022-01-14 12:01:59"):
        assert not await scheduler.get_task()
    with freeze_time("2022-01-14 12:02:01"):
        assert await scheduler.get_task() == task


@pytest.mark.parametrize("is_success", [True, False])
async def test_task_is_correctly_postponed(scheduler, task, is_success):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_task(task)

    with freeze_time("2022-01-14 12:00:00"):
        assert await scheduler.get_task() == task

    with freeze_time("2022-01-14 12:00:01"):
        await scheduler.release_task(task, is_success)
    with freeze_time("2022-01-14 12:00:02"):
        if is_success:
            assert not await scheduler.get_task()
        else:
            assert await scheduler.get_task() == task


async def test_task_is_available_after_append(scheduler, task):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_task(task)

    with freeze_time("2022-01-14 12:59:55"):
        assert await scheduler.get_task() == task


@pytest.mark.parametrize("is_success", [True, False])
async def test_task_append_do_not_break_schedule(scheduler, task, is_success):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_task(task)
    with freeze_time("2022-01-14 12:00:00"):
        assert await scheduler.get_task() == task
    with freeze_time("2022-01-14 12:00:01"):
        await scheduler.release_task(task, is_success)

    with freeze_time("2022-01-14 12:00:01"):
        await scheduler.append_task(task)

    with freeze_time("2022-01-14 12:00:01"):
        if is_success:
            assert not await scheduler.get_task()
        else:
            assert await scheduler.get_task() == task


async def test_renew_task_lock(scheduler, task):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_task(task)
    with freeze_time("2022-01-14 12:00:00"):
        assert await scheduler.get_task() == task
    with freeze_time("2022-01-14 12:01:00"):
        await scheduler.renew_task_lock(task)
    with freeze_time("2022-01-14 12:02:00"):
        await scheduler.renew_task_lock(task)
    with freeze_time("2022-01-14 12:03:00"):
        await scheduler.renew_task_lock(task)

    with freeze_time("2022-01-14 12:04:00"):
        assert not await scheduler.get_task()
    with freeze_time("2022-01-14 12:05:01"):
        assert await scheduler.get_task() == task


async def test_renew_task_lock__failed(scheduler, task):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_task(task)
    with freeze_time("2022-01-14 12:00:00"):
        assert await scheduler.get_task() == task
    with pytest.raises(RenewFailedError):
        with freeze_time("2022-01-14 12:05:00"):
            await scheduler.renew_task_lock(task)


if __name__ == "__main__":
    pytest.main()

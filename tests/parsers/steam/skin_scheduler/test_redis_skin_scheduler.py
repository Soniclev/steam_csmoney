import pytest
from freezegun import freeze_time

from price_monitoring.parsers.steam.skin_scheduler.redis_skin_scheduler import RedisSkinScheduler


@pytest.fixture()
def scheduler(fake_redis):
    return RedisSkinScheduler(fake_redis, "steam_skin_schedule")


async def test_get_skin__no_tasks(scheduler):
    assert not await scheduler.get_skin()


async def test_get_skin__append_skin(scheduler):
    await scheduler.append_market_name("AK")

    assert await scheduler.get_skin() == "AK"


async def test_get_skin__skin_is_not_available(scheduler):
    await scheduler.append_market_name("AK")

    await scheduler.get_skin()

    assert not await scheduler.get_skin()


async def test_delete_skin(scheduler):
    await scheduler.append_market_name("AK")
    await scheduler.delete_skin("AK")

    assert not await scheduler.get_skin()


@pytest.mark.parametrize("is_success", [True, False])
async def test_release_skin(scheduler, is_success):
    await scheduler.append_market_name("AK")
    assert await scheduler.get_skin() == "AK"

    await scheduler.release_skin("AK", is_success)

    if is_success:
        assert not await scheduler.get_skin()
    else:
        assert await scheduler.get_skin() == "AK"


async def test_skin_is_unlocked_after_time(scheduler):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_market_name("AK")

    with freeze_time("2022-01-14 12:00:00"):
        assert await scheduler.get_skin() == "AK"

    with freeze_time("2022-01-14 12:00:01"):
        assert not await scheduler.get_skin()
    with freeze_time("2022-01-14 12:01:00"):
        assert not await scheduler.get_skin()
    with freeze_time("2022-01-14 12:01:01"):
        assert await scheduler.get_skin() == "AK"


@pytest.mark.parametrize("is_success", [True, False])
async def test_skin_is_correctly_postponed(scheduler, is_success):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_market_name("AK")

    with freeze_time("2022-01-14 12:00:00"):
        assert await scheduler.get_skin() == "AK"

    with freeze_time("2022-01-14 12:00:01"):
        await scheduler.release_skin("AK", is_success)
    with freeze_time("2022-01-14 12:00:02"):
        if is_success:
            assert not await scheduler.get_skin()
        else:
            assert await scheduler.get_skin() == "AK"


async def test_skin_is_available_after_append(scheduler):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_market_name("AK")

    with freeze_time("2022-01-14 12:59:55"):
        assert await scheduler.get_skin() == "AK"


@pytest.mark.parametrize("is_success", [True, False])
async def test_skin_append_do_not_break_schedule(scheduler, is_success):
    with freeze_time("2022-01-14 11:59:55"):
        await scheduler.append_market_name("AK")
    with freeze_time("2022-01-14 12:00:00"):
        assert await scheduler.get_skin() == "AK"
    with freeze_time("2022-01-14 12:00:01"):
        await scheduler.release_skin("AK", is_success)

    with freeze_time("2022-01-14 12:00:01"):
        await scheduler.append_market_name("AK")

    with freeze_time("2022-01-14 12:00:01"):
        if is_success:
            assert not await scheduler.get_skin()
        else:
            assert await scheduler.get_skin() == "AK"


if __name__ == "__main__":
    pytest.main()

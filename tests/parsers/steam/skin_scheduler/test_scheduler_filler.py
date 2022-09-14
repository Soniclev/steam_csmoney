from unittest.mock import AsyncMock

import pytest

from price_monitoring.models.steam import MarketNamePack
from price_monitoring.parsers.steam.skin_scheduler.scheduler_filler import SchedulerFiller


@pytest.fixture()
def market_name_queue():
    return AsyncMock()


@pytest.fixture()
def skin_scheduler():
    return AsyncMock()


@pytest.fixture()
def parser(market_name_queue, skin_scheduler):
    return SchedulerFiller(market_name_queue, [skin_scheduler])


@pytest.mark.parametrize(
    "market_name, is_scheduled",
    [
        ("AK", True),
        (None, False),
    ],
)
async def test_run_market_name_reader(
    parser, market_name_queue, skin_scheduler, market_name, is_scheduled
):
    market_name_queue.get.return_value = (
        MarketNamePack(items=[market_name]) if market_name else None
    )

    await parser._run_market_name_reader()

    if is_scheduled:
        skin_scheduler.append_market_name.assert_awaited_with(market_name)
    else:
        assert skin_scheduler.append_market_name.call_count == 0


async def test_run(parser):
    parser._run_market_name_reader = AsyncMock()

    await parser.run()

    parser._run_market_name_reader.assert_awaited()


async def test_run__do_not_crash(parser, market_name_queue):
    market_name_queue.get.side_effect = Exception()

    await parser.run()


if __name__ == "__main__":
    pytest.main()

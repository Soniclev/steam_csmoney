from unittest.mock import AsyncMock

import pytest

from price_monitoring.parsers.steam.steam_sell_history_parser import SteamSellHistoryParser


@pytest.fixture()
def sell_history_parser():
    return AsyncMock()


@pytest.fixture()
def skin_scheduler():
    return AsyncMock()


@pytest.fixture()
def steam_result_queue():
    return AsyncMock()


@pytest.fixture()
def parser(sell_history_parser, skin_scheduler, steam_result_queue):
    return SteamSellHistoryParser(sell_history_parser, skin_scheduler, steam_result_queue)


@pytest.mark.parametrize(
    "market_name, is_success",
    [
        ("AK", True),
        ("AK", False),
        (None, None),
    ],
)
async def test_run_steam_parser(
    parser,
    sell_history_parser,
    steam_result_queue,
    skin_scheduler,
    market_name,
    is_success,
):
    skin_scheduler.get_skin.return_value = market_name
    sell_history_parser.fetch_history.return_value = is_success

    await parser._run_steam_parser()

    skin_scheduler.get_skin.assert_called()
    if market_name:
        sell_history_parser.fetch_history.assert_awaited_with(
            market_name=market_name, result_queue=steam_result_queue
        )
        skin_scheduler.release_skin.assert_awaited_with(market_name, is_success)
    else:
        sell_history_parser.fetch_history.assert_not_called()
        skin_scheduler.release_skin.assert_not_called()


async def test_run_steam_parser__with_error(
    parser, sell_history_parser, steam_result_queue, skin_scheduler
):
    skin_scheduler.get_skin.return_value = "AK"
    sell_history_parser.fetch_history.side_effect = Exception()

    await parser._run_steam_parser()

    skin_scheduler.release_skin.assert_awaited_with("AK", False)


async def test_run(parser):
    parser._run_steam_parser = AsyncMock()

    await parser.run()

    parser._run_steam_parser.assert_awaited()


async def test_run__do_not_crash(parser, skin_scheduler):
    skin_scheduler.get_skin.side_effect = Exception()

    await parser.run()


if __name__ == "__main__":
    pytest.main()

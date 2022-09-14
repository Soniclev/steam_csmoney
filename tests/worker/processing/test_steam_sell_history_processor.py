from unittest.mock import AsyncMock, patch, Mock

import pytest

from price_monitoring.models.steam import SteamSellHistory, SkinSellHistory
from price_monitoring.worker.processing.steam_sell_history_processor import (
    SteamSellHistoryProcessor,
)


@pytest.fixture()
def steam_order_storage():
    return AsyncMock()


@pytest.fixture()
def processor(steam_order_storage):
    return SteamSellHistoryProcessor(steam_order_storage)


async def test_process(processor, steam_order_storage):
    history = SteamSellHistory(
        market_name="AK", encoded_data='[["Mar 18 2016 01: +0",6.211,"120"]]'
    )
    summary = {1.01: 60, 1.02: 50}

    with patch(
        "price_monitoring.worker.processing.steam_sell_history_processor.SellHistoryAnalyzer"
    ) as stub:
        mock = Mock()
        mock.get_sold_amount_for_week.return_value = 125
        mock.is_stable.return_value = True
        mock.analyze_history.return_value = summary
        stub.return_value = mock
        await processor.process(history)

    steam_order_storage.update_skin.assert_called_with(
        SkinSellHistory(
            market_name=history.market_name,
            is_stable=True,
            sold_per_week=125,
            summary=summary,
        )
    )

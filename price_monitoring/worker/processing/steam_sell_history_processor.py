import datetime
import logging

from .abstract_steam_sell_history_processor import AbstractSteamSellHistoryProcessor
from .sell_history.analyzer import SellHistoryAnalyzer
from ...models.steam import SteamSellHistory, SkinSellHistory
from ...storage.steam import AbstractSteamSellHistoryStorage

logger = logging.getLogger(__name__)


class SteamSellHistoryProcessor(AbstractSteamSellHistoryProcessor):
    def __init__(self, steam_storage: AbstractSteamSellHistoryStorage):
        self._steam_storage = steam_storage

    async def process(self, history: SteamSellHistory) -> None:
        market_name = history.market_name

        analyzer = SellHistoryAnalyzer(history.encoded_data)
        current_dt = datetime.datetime.utcnow()
        is_stable = analyzer.is_stable(current_dt)
        sold_per_week = analyzer.get_sold_amount_for_week(current_dt)
        summary = analyzer.analyze_history(current_dt)

        logger.info(f"Sell history for {market_name}: {is_stable=} | {sold_per_week=} | {summary=}")

        await self._steam_storage.update_skin(
            SkinSellHistory(
                market_name=history.market_name,
                is_stable=is_stable,
                sold_per_week=sold_per_week,
                summary=summary,
            )
        )

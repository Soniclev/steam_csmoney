import logging

from .abstract_steam_processor import AbstractSteamSkinProcessor
from ...models.steam import SteamSkinHistogram
from ...storage.steam import AbstractSteamOrdersStorage

logger = logging.getLogger(__name__)


def _extract_buy_order(data: dict) -> float | None:
    if "highest_buy_order" in data:
        value = data["highest_buy_order"]
        if value:
            return int(value) / 100
    return None


def _extract_sell_order(data: dict) -> float | None:
    if "lowest_sell_order" in data:
        value = data["lowest_sell_order"]
        if value:
            return int(value) / 100
    return None


class SteamSkinProcessor(AbstractSteamSkinProcessor):
    def __init__(self, steam_order_storage: AbstractSteamOrdersStorage):
        self._steam_order_storage = steam_order_storage

    async def process(self, skin: SteamSkinHistogram) -> None:
        market_name = skin.market_name
        buy_order = _extract_buy_order(skin.response)
        sell_order = _extract_sell_order(skin.response)

        await self._steam_order_storage.update_skin_order(
            market_name=market_name, buy_order=buy_order, sell_order=sell_order
        )
        logger.info(f"Updated orders for {market_name}: {buy_order} and {sell_order}")

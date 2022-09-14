import logging
from typing import Sequence

from common.tracer import trace, annotate
from .abstract_offer_provider import AbstractOfferProvider
from ..offers import BaseItemOffer
from ..offers import SteamSellHistoryOffer
from ..steam_fee import SteamFee
from ...decorators import timer
from ...storage.csmoney import AbstractCsmoneyItemStorage
from ...storage.steam import AbstractSteamSellHistoryStorage

_MIN_SOLD_PER_WEEK = 5

logger = logging.getLogger(__name__)


def _get_percentile(price: float) -> float:
    return 50 if price < 100 else 20


class RedisSellHistoryProvider(AbstractOfferProvider):
    def __init__(self, steam: AbstractSteamSellHistoryStorage, csmoney: AbstractCsmoneyItemStorage):
        self.steam = steam
        self.csmoney = csmoney

    @timer(logger)
    @trace
    async def get_items(
        self, percentage_limit: float = None, min_price: float = None
    ) -> Sequence[BaseItemOffer]:
        is_trade_ban = self.csmoney.is_trade_ban
        csmoney_items = await self.csmoney.get_all()
        annotate(f"Loaded {len(csmoney_items)} items from cs.money")
        steam_items = await self.steam.get_all()
        annotate(f"Loaded {len(steam_items)} items from steam")

        items = []
        for history in steam_items.values():
            market_name = history.market_name
            if market_name not in csmoney_items:
                continue
            if not history.is_stable:
                continue
            if history.sold_per_week < _MIN_SOLD_PER_WEEK:
                continue
            csmoney_price = csmoney_items[market_name]
            if min_price and csmoney_price < min_price:
                continue
            percentile = _get_percentile(csmoney_price)
            price_50th = history.get(percentile)  # 50 for price < 100$; otherwise 30
            if not price_50th:
                continue
            offer = SteamSellHistoryOffer(
                market_name=market_name,
                orig_price=csmoney_price,
                suggested_price=SteamFee.subtract_fee(price_50th),
                mean_price=price_50th,
                sold_per_week=history.sold_per_week,
                lock_status="TRADEBAN" if is_trade_ban else None,
            )
            if percentage_limit and offer.compute_percentage() < percentage_limit:
                continue
            items.append(offer)

        return items

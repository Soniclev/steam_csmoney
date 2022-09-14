from typing import Sequence

from common.tracer import trace, annotate
from .abstract_offer_provider import AbstractOfferProvider
from ..offers import BaseItemOffer, SteamOrdersOffer
from ..steam_fee import SteamFee
from ...storage.csmoney import AbstractCsmoneyItemStorage
from ...storage.steam import AbstractSteamOrdersStorage


class RedisOfferProvider(AbstractOfferProvider):
    def __init__(self, steam: AbstractSteamOrdersStorage, csmoney: AbstractCsmoneyItemStorage):
        self.steam = steam
        self.csmoney = csmoney

    @trace
    async def get_items(
        self, percentage_limit: float = None, min_price: float = None
    ) -> Sequence[BaseItemOffer]:
        csmoney_items = await self.csmoney.get_all()
        annotate(f"Loaded {len(csmoney_items)} items from cs.money")
        steam_items = await self.steam.get_all()
        annotate(f"Loaded {len(steam_items)} items from steam")

        items = []
        for market_name, (buy_order, _) in steam_items.items():
            if not buy_order:
                continue
            if market_name not in csmoney_items:
                continue
            csmoney_price = csmoney_items[market_name]
            if min_price and csmoney_price < min_price:
                continue
            offer = SteamOrdersOffer(
                market_name=market_name,
                orig_price=csmoney_price,
                buy_order=SteamFee.subtract_fee(buy_order),
            )
            if percentage_limit is not None and offer.compute_percentage() < percentage_limit:
                continue
            items.append(offer)

        return items

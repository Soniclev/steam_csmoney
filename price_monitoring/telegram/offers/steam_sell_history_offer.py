from .base_item_offer import BaseItemOffer
from ..models import ItemOfferNotification
from ...types import MarketName


class SteamSellHistoryOffer(BaseItemOffer):
    def __init__(
        self,
        market_name: MarketName,
        orig_price: float,
        suggested_price: float,
        mean_price: float,
        sold_per_week: int,
        lock_status: str | None = None,
    ):
        super().__init__(market_name, orig_price, suggested_price)
        self.mean_price = mean_price
        self.sold_per_week = sold_per_week
        self.lock_status = lock_status

    def create_notification(self) -> ItemOfferNotification:
        obj = super().create_notification()
        obj.short_title = f"AVG ${self.mean_price} | {self.sold_per_week} SOLD IN WEEK"
        if self.lock_status:
            obj.short_title += f" | {self.lock_status}"
        return obj

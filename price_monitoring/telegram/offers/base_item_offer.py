from ..models import ItemOfferNotification
from ...types import MarketName


class BaseItemOffer:
    def __init__(self, market_name: MarketName, orig_price: float, sell_price: float):
        self.market_name = market_name
        self.orig_price = round(orig_price, 2)
        self.sell_price = round(sell_price, 2)

    def create_notification(self) -> ItemOfferNotification:
        return ItemOfferNotification(
            market_name=self.market_name,
            orig_price=self.orig_price,
            sell_price=self.sell_price,
            short_title="UNKNOWN",
        )

    def compute_difference(self) -> float:
        return round(self.sell_price - self.orig_price, 2)

    def compute_percentage(self) -> float:
        return round(self.compute_difference() / self.orig_price * 100, 2)

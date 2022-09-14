from .base_item_offer import BaseItemOffer
from ..models import ItemOfferNotification
from ...types import MarketName

AUTOBUY = "AUTOBUY"


class SteamOrdersOffer(BaseItemOffer):
    def __init__(self, market_name: MarketName, orig_price: float, buy_order: float):
        # pylint: disable=useless-super-delegation
        super().__init__(market_name, orig_price, buy_order)

    def create_notification(self) -> ItemOfferNotification:
        obj = super().create_notification()
        obj.short_title = AUTOBUY
        return obj

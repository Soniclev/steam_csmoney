from dataclasses import dataclass

from marshmallow_dataclass import add_schema

from common.core.dataclass_json import JsonMixin
from ..types import MarketName


@add_schema
@dataclass
class NotificationSettings(JsonMixin):
    max_threshold: float = 0
    min_price: float = 10


@add_schema
@dataclass
class ItemOfferNotification(JsonMixin):
    market_name: MarketName
    orig_price: float
    sell_price: float
    short_title: str

    def compute_percentage_diff(self) -> float:
        return round((self.sell_price - self.orig_price) / self.orig_price * 100, 2)

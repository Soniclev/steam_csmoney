from dataclasses import dataclass

from marshmallow_dataclass import add_schema

from common.core.dataclass_json import JsonMixin
from .csmoney import compute_accept_price
from ...types import MarketName


@add_schema
@dataclass
class OverpayReference(JsonMixin):
    market_name: MarketName
    float_: str
    overpay: float
    base_price: float
    sell_price: float

    def compute_accept_price(self) -> float:
        return compute_accept_price(self.base_price, self.overpay)

    def compute_profit(self) -> float:
        return compute_accept_price(self.base_price, self.overpay) - self.sell_price

    def compute_perc_profit(self) -> float:
        return round(self.compute_profit() / self.sell_price * 100, 2)

    def __str__(self):
        return (
            f"{self.market_name:70} {self.float_:20} {self.compute_accept_price():10.2f} "
            f"{self.sell_price:10.2f} {self.compute_perc_profit():10.2f}%"
        )

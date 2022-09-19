from dataclasses import dataclass, field

from marshmallow_dataclass import add_schema

from common.core.dataclass_json import JsonMixin, FastJsonMixin
from ..types import MarketName


@add_schema
@dataclass
class SteamSkinHistogram(JsonMixin):
    market_name: MarketName
    response: dict


@add_schema
@dataclass
class MarketNamePack(JsonMixin):
    items: list[MarketName] = field(default_factory=list)


@add_schema
@dataclass
class SteamSellHistory(JsonMixin):
    market_name: MarketName
    encoded_data: str


@add_schema
@dataclass
class SkinSellHistory(FastJsonMixin):
    market_name: MarketName
    is_stable: bool
    sold_per_week: int
    summary: dict[float, float]  # key: price; value: percentage cover

    def __init__(
        self,
        market_name: MarketName,
        is_stable: bool,
        sold_per_week: int,
        summary: dict[float, float] | dict[str, float],
    ):
        self.market_name = market_name
        self.is_stable = is_stable
        self.sold_per_week = sold_per_week
        self.summary = {float(k): v for k, v in summary.items()}

    def get(self, max_level: float) -> float | None:
        last = None
        for price, coverage in self.summary.items():
            if max_level <= coverage:
                last = price
            else:
                break
        return last

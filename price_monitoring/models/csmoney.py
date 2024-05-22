from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List

from marshmallow_dataclass import add_schema

from common.core.dataclass_json import JsonMixin
from ..types import MarketName, NameId


class CsmoneyItemCategory(Enum):
    KEY = 1
    KNIFE = 2
    RIFLE = 3
    SNIPER_RIFLE = 4
    PISTOL = 5
    SMG = 6
    SHOTGUN = 7
    MACHINE_GUN = 8
    PIN = 9
    STICKER = 10
    MUSIC_KIT = 11
    CASE = 12
    GLOVE = 13
    GRAFFITI = 14
    NAMETAG = 16
    AGENT = 18
    PATCH = 19
    ZEUS = 20


@add_schema
@dataclass
class CsmoneyItem(JsonMixin):
    name: MarketName
    price: float  # price including overpay
    asset_id: str
    name_id: NameId
    type_: CsmoneyItemCategory
    float_: Optional[str] = None
    unlock_timestamp: Optional[datetime] = None
    overpay_float: Optional[float] = None


@add_schema
@dataclass
class CsmoneyItemPack(JsonMixin):
    items: List[CsmoneyItem] = field(default_factory=list)


@add_schema
@dataclass
class CsmoneyTask(JsonMixin):
    # note that an offset parameter should be removed from a URL
    # e.g.: https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true
    url: str


@add_schema
@dataclass
class CsmoneyItemOverpay(JsonMixin):
    market_name: MarketName
    name_id: NameId
    float_: str
    overpay: float

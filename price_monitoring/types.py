from typing import TypeAlias

MarketName: TypeAlias = str
NameId: TypeAlias = int  # used on cs.money
ItemNameId: TypeAlias = int  # used on steam market
OrderPrice: TypeAlias = float | None
BuySellOrders: TypeAlias = tuple[OrderPrice, OrderPrice]

from abc import ABC, abstractmethod

from ...types import MarketName


class AbstractCsmoneyItemStorage(ABC):
    @abstractmethod
    async def update_item(self, market_name: MarketName, item_price: float) -> None:
        ...

    @abstractmethod
    async def get_all(self) -> dict[MarketName, float]:
        ...

    @property
    @abstractmethod
    def is_trade_ban(self) -> bool:
        ...

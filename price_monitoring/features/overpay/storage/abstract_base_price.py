from abc import ABC, abstractmethod

from ....types import MarketName


class AbstractBasePriceStorage(ABC):
    @abstractmethod
    async def update_item(self, market_name: MarketName, base_price: float):
        pass

    @abstractmethod
    async def get_all(self) -> dict[MarketName, float]:
        pass

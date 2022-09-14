from abc import abstractmethod, ABC

from ...types import MarketName, BuySellOrders


class AbstractSteamOrdersStorage(ABC):
    @abstractmethod
    async def get_all(self) -> dict[MarketName, BuySellOrders]:
        ...

    @abstractmethod
    async def update_skin_order(
        self, market_name: MarketName, buy_order: float | None, sell_order: float | None
    ) -> None:
        ...

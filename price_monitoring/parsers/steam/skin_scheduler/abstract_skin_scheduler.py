from abc import abstractmethod, ABC

from ....types import MarketName


class AbstractSkinScheduler(ABC):
    @abstractmethod
    async def append_market_name(self, market_name: MarketName):
        ...

    @abstractmethod
    async def get_skin(self) -> MarketName | None:
        ...

    @abstractmethod
    async def release_skin(self, market_name: MarketName, is_success: bool) -> None:
        ...

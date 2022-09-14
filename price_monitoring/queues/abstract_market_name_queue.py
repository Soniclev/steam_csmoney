from abc import abstractmethod, ABC

from ..models.steam import MarketNamePack


class AbstractMarketNameReader(ABC):
    @abstractmethod
    async def get(self, timeout: int = 5) -> MarketNamePack | None:
        ...


class AbstractMarketNameWriter(ABC):
    @abstractmethod
    async def put(self, pack: MarketNamePack) -> None:
        ...

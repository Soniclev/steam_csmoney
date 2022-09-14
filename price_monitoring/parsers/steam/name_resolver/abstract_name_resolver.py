from abc import abstractmethod, ABC

from ....types import MarketName, ItemNameId


class SkinNotFoundError(Exception):
    def __init__(self, market_name: MarketName):
        super().__init__()
        self._market_name = market_name

    def __str__(self):
        return self._market_name


class AbstractNameResolver(ABC):
    @abstractmethod
    async def resolve_market_name(self, market_name: MarketName) -> ItemNameId:
        ...

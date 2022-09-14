from abc import abstractmethod, ABC

from ..models.steam import SteamSellHistory


class AbstractSteamSellHistoryReader(ABC):
    @abstractmethod
    async def get(self, timeout: int = 5) -> SteamSellHistory | None:
        ...


class AbstractSteamSellHistoryWriter(ABC):
    @abstractmethod
    async def put(self, history: SteamSellHistory) -> None:
        ...

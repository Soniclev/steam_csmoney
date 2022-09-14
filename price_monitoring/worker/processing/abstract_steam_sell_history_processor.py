from abc import abstractmethod, ABC

from ...models.steam import SteamSellHistory


class AbstractSteamSellHistoryProcessor(ABC):
    @abstractmethod
    async def process(self, history: SteamSellHistory) -> None:
        ...

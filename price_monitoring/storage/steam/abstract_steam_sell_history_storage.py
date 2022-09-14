from abc import abstractmethod, ABC

from ...models.steam import SkinSellHistory
from ...types import MarketName


class AbstractSteamSellHistoryStorage(ABC):
    @abstractmethod
    async def get_all(self) -> dict[MarketName, SkinSellHistory]:
        ...

    @abstractmethod
    async def update_skin(self, history: SkinSellHistory) -> None:
        ...

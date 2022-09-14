from abc import abstractmethod, ABC

from ..models.steam import SteamSkinHistogram


class AbstractSteamOrderReader(ABC):
    @abstractmethod
    async def get(self, timeout: int = 5) -> SteamSkinHistogram | None:
        ...


class AbstractSteamOrderWriter(ABC):
    @abstractmethod
    async def put(self, skin: SteamSkinHistogram) -> None:
        ...

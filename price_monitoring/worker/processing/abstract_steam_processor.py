from abc import abstractmethod, ABC

from ...models.steam import SteamSkinHistogram


class AbstractSteamSkinProcessor(ABC):
    @abstractmethod
    async def process(self, skin: SteamSkinHistogram) -> None:
        ...

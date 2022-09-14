from abc import ABC, abstractmethod

from ....types import NameId


class AbstractBasePriceFetcher(ABC):
    @abstractmethod
    async def get(self, name_ids: list[NameId]) -> dict[NameId, float]:
        pass

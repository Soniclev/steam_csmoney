from abc import ABC, abstractmethod
from typing import Sequence

from ..offers import BaseItemOffer


class AbstractFilter(ABC):
    @abstractmethod
    async def filter_new_offers(self, offers: Sequence[BaseItemOffer]) -> Sequence[BaseItemOffer]:
        ...

    @abstractmethod
    async def append_offers(self, offers: Sequence[BaseItemOffer]) -> None:
        ...

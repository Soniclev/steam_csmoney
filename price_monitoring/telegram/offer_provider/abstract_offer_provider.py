from abc import ABC, abstractmethod
from typing import Sequence

from ..offers import BaseItemOffer


class AbstractOfferProvider(ABC):
    @abstractmethod
    async def get_items(
        self, percentage_limit: float = None, min_price: float = None
    ) -> Sequence[BaseItemOffer]:
        ...

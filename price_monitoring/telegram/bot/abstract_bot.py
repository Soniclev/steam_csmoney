from abc import ABC, abstractmethod

from ..models import ItemOfferNotification


class AbstractBot(ABC):
    @abstractmethod
    async def notify(self, notification: ItemOfferNotification) -> None:
        ...

from abc import ABC, abstractmethod

from ..models import NotificationSettings


class AbstractSettings(ABC):
    @abstractmethod
    async def get(self) -> NotificationSettings | None:
        ...

    @abstractmethod
    async def set(self, settings: NotificationSettings) -> None:
        ...

    @abstractmethod
    async def set_default(self) -> None:
        ...

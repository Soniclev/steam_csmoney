from abc import ABC, abstractmethod


class AbstractWhitelist(ABC):
    @abstractmethod
    async def add_member(self, member: int) -> None:
        ...

    @abstractmethod
    async def remove_member(self, member: int) -> None:
        ...

    @abstractmethod
    async def get_members(self) -> list[int]:
        ...

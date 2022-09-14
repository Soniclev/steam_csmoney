from abc import ABC, abstractmethod


class AbstractRunner(ABC):
    @abstractmethod
    async def run(self) -> None:
        ...

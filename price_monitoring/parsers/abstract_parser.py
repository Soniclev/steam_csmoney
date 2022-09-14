from abc import abstractmethod, ABC


class AbstractParser(ABC):
    @abstractmethod
    async def run(self) -> None:
        ...

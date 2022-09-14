from abc import ABC, abstractmethod

from ....queues import AbstractCsmoneyWriter


class MaxAttemptsReachedError(Exception):
    pass


class AbstractCsmoneyParser(ABC):
    @abstractmethod
    async def parse(
        self, url: str, result_queue: AbstractCsmoneyWriter, max_attempts: int = 10
    ) -> None:
        ...

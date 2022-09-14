from abc import ABC, abstractmethod

from ....queues import AbstractSteamSellHistoryWriter
from ....types import MarketName


class AbstractSellHistoryParser(ABC):
    @abstractmethod
    async def fetch_history(
        self, market_name: MarketName, result_queue: AbstractSteamSellHistoryWriter
    ) -> bool:
        ...

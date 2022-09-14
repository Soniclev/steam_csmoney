from abc import ABC, abstractmethod

from ....queues import AbstractSteamOrderWriter
from ....types import MarketName


class AbstractSteamOrdersParser(ABC):
    @abstractmethod
    async def fetch_orders(self, market_name: MarketName, result_queue: AbstractSteamOrderWriter):
        ...

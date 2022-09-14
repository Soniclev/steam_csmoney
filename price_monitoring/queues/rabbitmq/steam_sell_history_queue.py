from common.rpc.queue_publisher import QueuePublisher
from common.rpc.queue_reader import QueueReader
from ..abstract_steam_sell_history_queue import (
    AbstractSteamSellHistoryReader,
    AbstractSteamSellHistoryWriter,
)
from ...models.steam import SteamSellHistory


class SteamSellHistoryReader(AbstractSteamSellHistoryReader):
    def __init__(self, reader: QueueReader):
        self._reader = reader

    async def get(self, timeout: int = 5) -> SteamSellHistory | None:
        data = await self._reader.read(timeout=timeout)
        if data:
            return SteamSellHistory.load_bytes(data)
        return None


class SteamSellHistoryWriter(AbstractSteamSellHistoryWriter):
    def __init__(self, publisher: QueuePublisher):
        self._publisher = publisher

    async def put(self, history: SteamSellHistory) -> None:
        data = history.dump_bytes()
        await self._publisher.publish(data)

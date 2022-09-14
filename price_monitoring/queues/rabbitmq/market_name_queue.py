from common.rpc.queue_publisher import QueuePublisher
from common.rpc.queue_reader import QueueReader
from ..abstract_market_name_queue import (
    AbstractMarketNameReader,
    AbstractMarketNameWriter,
)
from ...models.steam import MarketNamePack


class MarketNameReader(AbstractMarketNameReader):
    def __init__(self, reader: QueueReader):
        self._reader = reader

    async def get(self, timeout: int = 5) -> MarketNamePack | None:
        data = await self._reader.read(timeout=timeout)
        if data:
            return MarketNamePack.load_bytes(data)
        return None


class MarketNameWriter(AbstractMarketNameWriter):
    def __init__(self, publisher: QueuePublisher):
        self._publisher = publisher

    async def put(self, pack: MarketNamePack) -> None:
        data = pack.dump_bytes()
        await self._publisher.publish(data)

from common.rpc.queue_publisher import QueuePublisher
from common.rpc.queue_reader import QueueReader
from ..abstract_steam_order_queue import (
    AbstractSteamOrderReader,
    AbstractSteamOrderWriter,
)
from ...models.steam import SteamSkinHistogram


class SteamOrderReader(AbstractSteamOrderReader):
    def __init__(self, reader: QueueReader):
        self._reader = reader

    async def get(self, timeout: int = 5) -> SteamSkinHistogram | None:
        data = await self._reader.read(timeout=timeout)
        if data:
            return SteamSkinHistogram.load_bytes(data)
        return None


class SteamOrderWriter(AbstractSteamOrderWriter):
    def __init__(self, publisher: QueuePublisher):
        self._publisher = publisher

    async def put(self, skin: SteamSkinHistogram) -> None:
        data = skin.dump_bytes()
        await self._publisher.publish(data)

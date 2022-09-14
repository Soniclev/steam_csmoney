from common.rpc.queue_publisher import QueuePublisher
from common.rpc.queue_reader import QueueReader
from ..abstract_csmoney_result_queue import AbstractCsmoneyReader, AbstractCsmoneyWriter
from ...models.csmoney import CsmoneyItemPack


class CsmoneyReader(AbstractCsmoneyReader):
    def __init__(self, reader: QueueReader):
        self._reader = reader

    async def get(self, timeout: int = 5) -> CsmoneyItemPack | None:
        data = await self._reader.read(timeout=timeout)
        if data:
            return CsmoneyItemPack.load_bytes(data)
        return None


class CsmoneyWriter(AbstractCsmoneyWriter):
    def __init__(self, publisher: QueuePublisher):
        self._publisher = publisher

    async def put(self, item: CsmoneyItemPack) -> None:
        data = item.dump_bytes()
        await self._publisher.publish(data)

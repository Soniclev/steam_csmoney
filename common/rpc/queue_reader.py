import asyncio.exceptions
from asyncio import QueueEmpty
from datetime import timedelta
from typing import Optional

from aio_pika import Channel


class QueueReader:
    def __init__(self, name: str,
                 channel: Channel,
                 passive: bool = False,
                 message_ttl: Optional[timedelta] = None):
        self._name = name
        self._channel = channel
        self._passive = passive
        self._queue = None
        self._message_ttl = message_ttl

    async def connect(self):
        arguments = {}
        if self._message_ttl:
            arguments['x-message-ttl'] = int(self._message_ttl.total_seconds())
        self._queue = await self._channel.declare_queue(
            name=self._name,
            passive=self._passive,
            arguments=arguments
        )
        return self

    async def read(self, timeout: int = 5) -> Optional[bytes]:
        try:
            msg = await self._queue.get(timeout=timeout, no_ack=True)
            return msg.body
        except (QueueEmpty, asyncio.exceptions.TimeoutError):
            pass

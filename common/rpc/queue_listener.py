from datetime import timedelta
from typing import Optional, Callable

from aio_pika import Channel


class QueueListener:
    def __init__(self, name: str,
                 channel: Channel,
                 on_msg: Optional[Callable],
                 passive: bool = False,
                 message_ttl: Optional[timedelta] = None):
        self._name = name
        self._channel = channel
        self._on_msg = on_msg
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
        await self._queue.consume(self._on_msg)
        return self

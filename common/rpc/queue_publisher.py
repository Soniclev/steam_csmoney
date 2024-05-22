from datetime import timedelta
from typing import Optional

from aio_pika import Channel, Message


class QueuePublisher:
    def __init__(self,
                 name: str,
                 channel: Channel,
                 passive: bool = False,
                 message_ttl: Optional[timedelta] = None):
        self.name = name
        self.channel = channel
        self.passive = passive
        self.message_ttl = message_ttl

    async def connect(self):
        arguments = {}
        if self.message_ttl:
            arguments['x-message-ttl'] = int(self.message_ttl.total_seconds())
        await self.channel.declare_queue(
            name=self.name,
            passive=self.passive,
            arguments=arguments
        )
        return self

    async def publish(self,
                      body: bytes,
                      timeout: float = 30,
                      message_ttl: Optional[timedelta] = None
                      ) -> None:
        expiration = (message_ttl.total_seconds() * 1000) if message_ttl else None
        await self.channel.default_exchange.publish(
            Message(body, expiration=expiration),
            routing_key=self.name,
            timeout=timeout
        )

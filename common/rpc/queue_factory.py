from datetime import timedelta
from typing import Optional, Callable

from .queue_listener import QueueListener
from .queue_publisher import QueuePublisher
from .queue_reader import QueueReader
from .rabbitmq_client import RabbitMQClient


class QueueFactory:
    @staticmethod
    async def connect_reader(name: str,
                             client: RabbitMQClient,
                             passive: bool = False,
                             message_ttl: Optional[timedelta] = None
                             ) -> QueueReader:
        channel = await client.create_channel()
        return await QueueReader(name=name,
                                 channel=channel,
                                 passive=passive,
                                 message_ttl=message_ttl
                                 ).connect()

    @staticmethod
    async def connect_listener(name: str,
                               client: RabbitMQClient,
                               on_msg: Optional[Callable],
                               passive: bool = False,
                               message_ttl: Optional[timedelta] = None
                               ) -> QueueListener:
        channel = await client.create_channel()
        return await QueueListener(name=name,
                                   channel=channel,
                                   on_msg=on_msg,
                                   passive=passive,
                                   message_ttl=message_ttl
                                   ).connect()

    @staticmethod
    async def connect_publisher(name: str,
                                client: RabbitMQClient,
                                passive: bool = False,
                                message_ttl: Optional[timedelta] = None
                                ) -> QueuePublisher:
        channel = await client.create_channel()
        return await QueuePublisher(name=name,
                                    channel=channel,
                                    passive=passive,
                                    message_ttl=message_ttl
                                    ).connect()

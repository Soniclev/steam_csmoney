import asyncio
import uuid
from typing import Callable, Optional

from aio_pika import IncomingMessage, Message, Channel


def _get_rkey(node_id: str, service: str):
    return f"{node_id}.{service}"


class MessageChannel:
    def __init__(self,
                 node_id: str,
                 service: str,
                 channel: Channel,
                 on_msg: Optional[Callable],
                 on_ask: Optional[Callable]):
        self.node_id = node_id
        self.service = service
        self.channel = channel
        self.on_msg = on_msg
        self.on_ask = on_ask
        self.futures = {}
        self.callback_queue = None

    async def connect(self):
        queue_name = _get_rkey(self.node_id, self.service)
        self.callback_queue = await self.channel.declare_queue(name=queue_name, exclusive=True)
        await self.callback_queue.consume(self._on_response)
        return self

    async def _on_response(self, message: IncomingMessage):
        if message.correlation_id:
            if message.headers and 'msg' in message.headers and message.headers['msg'] == 'request':
                await self.on_ask(self, message)
            else:
                future = self.futures.pop(message.correlation_id)
                future.set_result(message.body)
            return
        await self.on_msg(self, message)

    async def ask(self, node_id: str, service: str, body: bytes, timeout: float = 10) -> bytes:
        rkey = _get_rkey(node_id, service)
        correlation_id = str(uuid.uuid4())
        future = asyncio.get_running_loop().create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                body,
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
                headers={'msg': 'request'},
                expiration=timeout*1000
            ),
            routing_key=rkey,
            timeout=timeout
        )

        return await asyncio.wait_for(future, timeout=timeout)

    async def tell(self, node_id: str, service: str, body: bytes, timeout: float = 10) -> None:
        rkey = _get_rkey(node_id, service)

        await self.channel.default_exchange.publish(
            Message(body, expiration=timeout*1000),
            routing_key=rkey,
            timeout=timeout
        )

    async def respond(self, ask_msg: IncomingMessage, body: bytes, timeout: float = 10) -> None:
        await self.channel.default_exchange.publish(
            Message(
                body=body,
                correlation_id=ask_msg.correlation_id,
                expiration=timeout*1000
            ),
            routing_key=ask_msg.reply_to,
            timeout=timeout
        )

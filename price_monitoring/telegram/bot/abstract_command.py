from abc import ABC, abstractmethod
from typing import Iterable

from aiogram import Dispatcher, types


class AbstractCommand(ABC):
    def __init__(self, name: str):
        self.name = name

    def register_command(self, dispatcher: Dispatcher, members: Iterable[int]):
        dispatcher.message_handler(commands=[self.name], user_id=members)(self.handler)

    @abstractmethod
    async def handler(self, message: types.Message) -> None:
        ...

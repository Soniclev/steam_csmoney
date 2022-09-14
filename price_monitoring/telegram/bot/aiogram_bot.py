import asyncio
from typing import Iterable

import aiogram
from aiogram.types import ParseMode

from .abstract_bot import AbstractBot
from .abstract_command import AbstractCommand
from .abstract_whitelist import AbstractWhitelist
from .notification_formatter import to_markdown
from ..models import ItemOfferNotification


class AiogramBot(AbstractBot):
    def __init__(
        self,
        token: str,
        whitelist: AbstractWhitelist,
        commands: Iterable[AbstractCommand],
    ):
        self._whitelist = whitelist
        self.commands = commands
        self._bot = aiogram.Bot(token=token)
        self._dispatcher = aiogram.Dispatcher(self._bot)
        self._polling_task = None

    async def start(self):
        members = await self._whitelist.get_members()
        for command in self.commands:
            command.register_command(self._dispatcher, members)
        self._polling_task = asyncio.create_task(self._dispatcher.start_polling())

    async def notify(self, notification: ItemOfferNotification):
        await asyncio.gather(
            *[
                asyncio.create_task(
                    self._bot.send_message(
                        chat_id=member,
                        text=to_markdown(notification),
                        parse_mode=ParseMode.MARKDOWN_V2,
                        disable_web_page_preview=True,
                    )
                )
                for member in await self._whitelist.get_members()
            ]
        )

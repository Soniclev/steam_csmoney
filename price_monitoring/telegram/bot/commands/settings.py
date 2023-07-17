from aiogram import types

from ..abstract_command import AbstractCommand
from ..abstract_settings import AbstractSettings

_COMMAND = "settings"


class Settings(AbstractCommand):
    def __init__(self, settings_provider: AbstractSettings):
        super().__init__(_COMMAND)
        self.settings_provider = settings_provider

    async def handler(self, message: types.Message) -> None:
        try:
            settings = await self.settings_provider.get()

            result = f"Current settings: {str(settings)}"

            await message.reply(result)
        except Exception as exc:
            await message.reply(str(exc))

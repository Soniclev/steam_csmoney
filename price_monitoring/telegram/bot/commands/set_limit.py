from aiogram import types

from ..abstract_command import AbstractCommand
from ..abstract_settings import AbstractSettings

_COMMAND = "set_limit"


class SetLimit(AbstractCommand):
    def __init__(self, settings_provider: AbstractSettings):
        super().__init__(_COMMAND)
        self.settings_provider = settings_provider

    async def handler(self, message: types.Message) -> None:
        try:
            args = message.get_args()
            try:
                percentage = float(args.split()[0])
            except Exception as exc:
                raise ValueError(f"could not convert string to float: '{args}'") from exc

            settings = await self.settings_provider.get()
            if not settings:
                raise ValueError("Не удалось загрузить настройки!")
            settings.max_threshold = percentage
            await self.settings_provider.set(settings)

            result = f"Лимит в {percentage}% успешно установлен!"

            await message.reply(result)
        except Exception as exc:
            await message.reply(str(exc))

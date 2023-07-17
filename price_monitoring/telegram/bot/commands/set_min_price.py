from aiogram import types

from ..abstract_command import AbstractCommand
from ..abstract_settings import AbstractSettings

_COMMAND = "set_min_price"


class SetMinPrice(AbstractCommand):
    def __init__(self, settings_provider: AbstractSettings):
        super().__init__(_COMMAND)
        self.settings_provider = settings_provider

    async def handler(self, message: types.Message) -> None:
        try:
            args = message.get_args()
            try:
                min_price = float(args.split()[0])
            except Exception as exc:
                raise ValueError(f"could not convert string to float: '{args}'") from exc

            if min_price < 0:
                raise ValueError("Negative values are not allowed!")

            settings = await self.settings_provider.get()
            if not settings:
                raise ValueError("Failed to load settings!")
            settings.min_price = min_price
            await self.settings_provider.set(settings)

            result = f"Minimal price ${min_price} successfully set!"

            await message.reply(result)
        except Exception as exc:
            await message.reply(str(exc))

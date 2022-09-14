import logging

import aiogram.utils.parts
from aiogram import types
from aiogram.types import ParseMode

from common.tracer import trace, annotate
from ..abstract_command import AbstractCommand
from ..notification_formatter import several_to_markdown
from ...offer_provider import AbstractOfferProvider
from ...offers import BaseItemOffer

_COMMAND = "offers"


def _key(offer: BaseItemOffer):
    return offer.compute_percentage()


class Offers(AbstractCommand):
    def __init__(self, offer_provider: AbstractOfferProvider):
        super().__init__(_COMMAND)
        self.offer_provider = offer_provider

    @trace
    async def handler(self, message: types.Message) -> None:
        try:
            offers = await self.offer_provider.get_items()
            annotate(f"Loaded {len(offers)} offers")

            sorted_offers = sorted(offers, key=_key, reverse=True)

            result = "Текущие предложения:\n"
            result += several_to_markdown(offer.create_notification() for offer in sorted_offers)
            parts = aiogram.utils.parts.safe_split_text(result, split_separator="\n\n")

            # Strictly follow original ordering, because offers sorted by profitability
            for part in parts:
                await message.reply(
                    part,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True,
                )
        except Exception as exc:
            logging.error('There was an error while handling "/offers" command.', exc_info=exc)
            await message.reply(str(exc))

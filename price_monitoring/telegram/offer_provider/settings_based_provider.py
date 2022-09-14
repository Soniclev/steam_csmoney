from typing import Sequence

from common.tracer import trace
from .abstract_offer_provider import AbstractOfferProvider
from ..bot import AbstractSettings
from ..offers import BaseItemOffer


class SettingsBasedProvider(AbstractOfferProvider):
    def __init__(self, settings_provider: AbstractSettings, offer_provider: AbstractOfferProvider):
        self.settings_provider = settings_provider
        self.offer_provider = offer_provider

    @trace
    async def get_items(
        self, percentage_limit: float = None, min_price: float = None
    ) -> Sequence[BaseItemOffer]:
        settings = await self.settings_provider.get()
        if not settings:
            raise ValueError("Failed to load settings!")
        return await self.offer_provider.get_items(
            percentage_limit=percentage_limit or settings.max_threshold,
            min_price=min_price or settings.min_price,
        )

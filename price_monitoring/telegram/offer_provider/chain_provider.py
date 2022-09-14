import asyncio
import typing

from common.tracer import trace
from .abstract_offer_provider import AbstractOfferProvider
from ..offers import BaseItemOffer


class ChainProvider(AbstractOfferProvider):
    def __init__(self, offer_providers: typing.Iterable[AbstractOfferProvider]):
        self.offer_providers = offer_providers

    @trace
    async def get_items(
        self, percentage_limit: float = None, min_price: float = None
    ) -> list[BaseItemOffer]:
        result = []
        for array in await asyncio.gather(
            *[
                provider.get_items(percentage_limit=percentage_limit, min_price=min_price)
                for provider in self.offer_providers
            ]
        ):
            result.extend(array)
        return result

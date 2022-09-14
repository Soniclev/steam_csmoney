from .abstract_name_resolver import AbstractNameResolver, SkinNotFoundError
from ....types import MarketName, ItemNameId


class MemoryCachedNameResolver(AbstractNameResolver):
    def __init__(self, resolver: AbstractNameResolver):
        self._resolver = resolver
        self._cache: dict[str, ItemNameId] = {}

    async def resolve_market_name(self, market_name: MarketName) -> ItemNameId:
        if market_name not in self._cache:
            try:
                self._cache[market_name] = await self._resolver.resolve_market_name(market_name)
            except SkinNotFoundError:
                self._cache[market_name] = -1
        if self._cache[market_name] == -1:
            raise SkinNotFoundError(market_name)
        return self._cache[market_name]

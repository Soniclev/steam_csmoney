from unittest.mock import AsyncMock

from price_monitoring.telegram.offer_provider.chain_provider import ChainProvider


async def test_get_items__existence():
    provider1 = AsyncMock()
    provider1.get_items.return_value = [1]
    provider2 = AsyncMock()
    provider2.get_items.return_value = [2]
    provider = ChainProvider([provider1, provider2])

    items = await provider.get_items(-100)

    assert set(items) == {1, 2}

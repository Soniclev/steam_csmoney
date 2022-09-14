from unittest.mock import AsyncMock

import pytest

from price_monitoring.parsers.steam.name_resolver.abstract_name_resolver import SkinNotFoundError
from price_monitoring.parsers.steam.name_resolver.memory_cached_name_resolver import (
    MemoryCachedNameResolver,
)


@pytest.fixture()
def root_resolver():
    return AsyncMock()


@pytest.fixture()
def name_resolver(root_resolver):
    return MemoryCachedNameResolver(root_resolver)


async def test_resolve__not_cached(name_resolver, root_resolver):
    root_resolver.resolve_market_name.return_value = 123

    name_id = await name_resolver.resolve_market_name("AK")

    assert name_id == 123
    root_resolver.resolve_market_name.assert_called_with("AK")


async def test_resolve__cached(name_resolver, root_resolver):
    root_resolver.resolve_market_name.return_value = 123

    name_ids = []
    for _ in range(10):
        name_ids.append(await name_resolver.resolve_market_name("AK"))

    for name_id in name_ids:
        assert name_id == 123
    assert root_resolver.resolve_market_name.call_count == 1
    root_resolver.resolve_market_name.assert_called_with("AK")


async def test_resolve__not_existed_skin__not_cached(name_resolver, root_resolver):
    root_resolver.resolve_market_name.side_effect = SkinNotFoundError("AK")

    with pytest.raises(SkinNotFoundError, match="AK"):
        await name_resolver.resolve_market_name("AK")

    assert root_resolver.resolve_market_name.call_count == 1
    root_resolver.resolve_market_name.assert_called_with("AK")


async def test_resolve__not_existed_skin__cached(name_resolver, root_resolver):
    root_resolver.resolve_market_name.side_effect = SkinNotFoundError("AK")

    for _ in range(10):
        with pytest.raises(SkinNotFoundError, match="AK"):
            await name_resolver.resolve_market_name("AK")

    assert root_resolver.resolve_market_name.call_count == 1
    root_resolver.resolve_market_name.assert_called_with("AK")


if __name__ == "__main__":
    pytest.main()

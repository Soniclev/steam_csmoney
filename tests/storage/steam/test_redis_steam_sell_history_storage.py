import pytest

from price_monitoring.models.steam import SkinSellHistory
from price_monitoring.storage.steam import RedisSteamSellHistoryStorage
from price_monitoring.storage.steam.redis_steam_sell_history_storage import (
    _key,
    _extract_market_name,
)


@pytest.mark.parametrize(
    "key,name",
    [
        (
            "prices:csmoney:★ StatTrak™ M9 Bayonet | Crimson Web (Factory New)",
            "★ StatTrak™ M9 Bayonet | Crimson Web (Factory New)",
        ),
        (
            "prices:csmoney:★ Sport Gloves | Vice (Factory New)",
            "★ Sport Gloves | Vice (Factory New)",
        ),
        (
            "prices:csmoney:Music Kit | Scarlxrd: King, Scar",
            "Music Kit | Scarlxrd: King, Scar",
        ),
    ],
)
def test_extract_market_name(key, name):
    assert _extract_market_name(key) == name


@pytest.fixture()
def storage(fake_redis):
    return RedisSteamSellHistoryStorage(fake_redis)


async def test_empty(storage):
    assert await storage.get_all() == {}


_history1 = SkinSellHistory(
    market_name="AK",
    is_stable=True,
    sold_per_week=125,
    summary={},
)
_history2 = SkinSellHistory(
    market_name="AK",
    is_stable=False,
    sold_per_week=25,
    summary={},
)


async def test_update(storage):
    await storage.update_skin(_history1)

    assert await storage.get_all() == {"AK": _history1}


async def test_several_update(storage):
    await storage.update_skin(_history1)
    await storage.update_skin(_history2)

    assert await storage.get_all() == {"AK": _history2}


async def test_ttl(fake_redis, storage):
    await storage.update_skin(_history1)

    assert await fake_redis.ttl(_key("AK")) > 0

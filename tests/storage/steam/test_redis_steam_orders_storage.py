import pytest

from price_monitoring.storage.steam import RedisSteamOrdersStorage
from price_monitoring.storage.steam.redis_steam_orders_storage import (
    _extract_orders,
    _key,
    _extract_market_name,
)


@pytest.mark.parametrize(
    "key,buy,sell",
    [
        ("1:2", 1, 2),
        ("0.23:0.26", 0.23, 0.26),
        ("None:0.26", None, 0.26),
        ("0.23:None", 0.23, None),
        ("None:None", None, None),
    ],
)
def test_extract_orders(key, buy, sell):
    assert _extract_orders(key) == (buy, sell)


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
    return RedisSteamOrdersStorage(fake_redis)


async def test_empty(storage):
    assert await storage.get_all() == {}


async def test_update(storage):
    await storage.update_skin_order("AK", 1.05, 1.07)

    assert await storage.get_all() == {"AK": (1.05, 1.07)}


async def test_several_update(storage):
    await storage.update_skin_order("AK", 1.05, 1.07)
    await storage.update_skin_order("AK", 1.06, 1.09)

    assert await storage.get_all() == {"AK": (1.06, 1.09)}


async def test_ttl(fake_redis, storage):
    await storage.update_skin_order("AK", 1.05, 1.07)

    assert await fake_redis.ttl(_key("AK")) > 0

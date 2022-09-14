import pytest

from price_monitoring.storage.csmoney import RedisCsmoneyItemStorage
from price_monitoring.storage.csmoney.redis_csmoney_item_storage import (
    _extract_price,
    _extract_market_name,
    _key,
)

KEY_PREFIX = "prices:csmoney:locked:"


@pytest.mark.parametrize(
    "key,name",
    [
        (
            "prices:csmoney:locked:★ StatTrak™ M9 Bayonet | Crimson Web (Factory New):1",
            "★ StatTrak™ M9 Bayonet | Crimson Web (Factory New)",
        ),
        (
            "prices:csmoney:locked:★ Sport Gloves | Vice (Factory New):0.23",
            "★ Sport Gloves | Vice (Factory New)",
        ),
        (
            "prices:csmoney:locked:Music Kit | Scarlxrd: King, Scar:0.23",
            "Music Kit | Scarlxrd: King, Scar",
        ),
    ],
)
def test_extract_market_name(key, name):
    assert _extract_market_name(KEY_PREFIX, key) == name


@pytest.mark.parametrize(
    "key,price",
    [
        ("prices:csmoney:locked:AK:1", 1),
        ("prices:csmoney:locked:AK:0.23", 0.23),
        ("prices:csmoney:locked:Music Kit | Scarlxrd: King, Scar:0.34", 0.34),
    ],
)
def test_extract_price(key, price):
    assert _extract_price(KEY_PREFIX, key) == price


@pytest.fixture()
def storage(fake_redis):
    return RedisCsmoneyItemStorage(fake_redis, KEY_PREFIX, True)


async def test_empty(storage):
    assert await storage.get_all() == {}


async def test_update(storage):
    await storage.update_item("AK", 0.6)

    assert await storage.get_all() == {"AK": 0.6}


async def test_several_update(storage):
    await storage.update_item("AK", 0.6)
    await storage.update_item("AK", 0.7)

    assert await storage.get_all() == {"AK": 0.6}


async def test_several_update_2(storage):
    await storage.update_item("AK", 0.6)
    await storage.update_item("AK", 0.7)
    await storage.update_item("AK", 0.5)

    assert await storage.get_all() == {"AK": 0.5}


async def test_ttl(fake_redis, storage):
    await storage.update_item("AK", 1)

    assert await fake_redis.ttl(_key(KEY_PREFIX, "AK", 1)) > 0


@pytest.mark.parametrize("trade_ban", [True, False])
def test_is_trade_ban(fake_redis, trade_ban):
    assert RedisCsmoneyItemStorage(fake_redis, KEY_PREFIX, trade_ban).is_trade_ban == trade_ban

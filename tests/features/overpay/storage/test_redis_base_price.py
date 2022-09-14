import pytest

from price_monitoring.features.overpay.storage import RedisBasePriceStorage
from price_monitoring.features.overpay.storage.redis_base_price import _key


@pytest.fixture()
def storage(fake_redis):
    return RedisBasePriceStorage(fake_redis)


async def test_empty(storage):
    assert await storage.get_all() == {}


async def test_update(storage):
    await storage.update_item("AK", 0.6)

    assert await storage.get_all() == {"AK": 0.6}


async def test_several_update(storage):
    await storage.update_item("AK", 0.6)
    await storage.update_item("AK", 0.7)

    assert await storage.get_all() == {"AK": 0.7}


async def test_several_update_2(storage):
    await storage.update_item("AK", 0.5)
    await storage.update_item("AK", 0.7)
    await storage.update_item("AK", 0.6)

    assert await storage.get_all() == {"AK": 0.6}


async def test_ttl(fake_redis, storage):
    await storage.update_item("AK", 1)

    assert await fake_redis.ttl(_key("AK")) > 0


if __name__ == "__main__":
    pytest.main()

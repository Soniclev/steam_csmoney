import pytest

from price_monitoring.features.overpay.storage.redis_overpay import _key, RedisOverpayStorage
from price_monitoring.models.csmoney import CsmoneyItemOverpay

overpay = CsmoneyItemOverpay(market_name="AK", float_="0.001", name_id=1, overpay=0.51)


@pytest.fixture()
def storage(fake_redis):
    return RedisOverpayStorage(fake_redis)


async def test_empty(storage):
    assert await storage.get_all() == []


async def test_update(storage):
    await storage.add_overpay(overpay)

    assert await storage.get_all() == [overpay]


async def test_several_update(storage):
    await storage.add_overpay(overpay)
    overpay2 = CsmoneyItemOverpay(market_name="AK", float_="0.001", name_id=1, overpay=0.49)
    await storage.add_overpay(overpay2)

    assert await storage.get_all() == [overpay2]


async def test_several_update_2(storage):
    overpay2 = CsmoneyItemOverpay(market_name="AK", float_="0.0012", name_id=1, overpay=0.51)
    await storage.add_overpay(overpay)
    await storage.add_overpay(overpay2)

    assert await storage.get_all() == [overpay, overpay2]


async def test_ttl(fake_redis, storage):
    await storage.add_overpay(overpay)

    assert await fake_redis.ttl(_key("AK", "0.001")) > 0


if __name__ == "__main__":
    pytest.main()

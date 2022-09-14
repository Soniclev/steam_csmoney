import pytest

from price_monitoring.telegram.bot.redis_settings import RedisSettings
from price_monitoring.telegram.models import NotificationSettings


@pytest.fixture()
def storage(fake_redis):
    return RedisSettings(fake_redis, "key123")


async def test__right_key_used(storage, fake_redis):
    await storage.set_default()

    assert await fake_redis.keys() == [b"key123"]


async def test_get__empty(storage):
    assert await storage.get() is None


async def test_set(storage):
    default = NotificationSettings()

    await storage.set(default)

    assert await storage.get() == default


async def test_set_default(storage):
    default = NotificationSettings()

    await storage.set_default()

    assert await storage.get() == default

import pytest

from price_monitoring.telegram.bot.redis_whitelist import RedisWhitelist


@pytest.fixture
def whitelist(fake_redis):
    return RedisWhitelist(fake_redis, "key123")


async def test_key(whitelist, fake_redis):
    await whitelist.add_member(1)

    keys = await fake_redis.keys("*")

    assert keys == [b"key123"]


async def test_add_member_and_get_members(whitelist, fake_redis):
    await whitelist.add_member(1)
    await whitelist.add_member(7)
    await whitelist.add_member(4)
    result = await whitelist.get_members()

    assert len(result) == 3
    for i in [1, 7, 4]:
        assert i in result
    assert all(isinstance(x, int) for x in result)


async def test_get_members__no_members(whitelist, fake_redis):
    result = await whitelist.get_members()

    assert result == []


async def test_remove_member(whitelist, fake_redis):
    await whitelist.add_member(1)
    await whitelist.add_member(7)

    await whitelist.remove_member(1)
    result = await whitelist.get_members()

    assert result == [7]

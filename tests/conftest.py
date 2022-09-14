import asyncio
from unittest import mock

import fakeredis.aioredis
import pytest

from price_monitoring import decorators


@pytest.fixture()
def fake_redis():
    redis = fakeredis.aioredis.FakeRedis()
    yield redis
    redis.close()


@pytest.fixture()
def disable_asyncio_sleep():
    orig = asyncio.sleep

    # noinspection PyUnusedLocal
    async def _mock(*args, **kwargs):
        await orig(0)

    with mock.patch("asyncio.sleep", new=_mock):
        yield


@pytest.fixture(scope="session", autouse=True)
def disable_infinite_loop():
    decorators._INFINITE_RUN = False
    yield
    decorators._INFINITE_RUN = True

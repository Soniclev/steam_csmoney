import pytest

from proxy_http.proxy import Proxy
from price_monitoring.storage.proxy import RedisProxyStorage

_KEY = "common_proxies"
_PROXIES = [Proxy(proxy=f"https://1.1.1.1:{port}") for port in range(100, 105)]


@pytest.fixture()
def storage(fake_redis):
    return RedisProxyStorage(fake_redis, _KEY)


async def test_add_and_get_all(storage):
    for proxy in _PROXIES:
        await storage.add(proxy)

    result = await storage.get_all()
    assert len(result) == len(_PROXIES)
    for proxy in _PROXIES:
        assert proxy in result


async def test_remove(storage):
    await storage.add(_PROXIES[0])
    await storage.add(_PROXIES[1])

    await storage.remove(_PROXIES[1])

    result = await storage.get_all()
    assert result == [_PROXIES[0]]

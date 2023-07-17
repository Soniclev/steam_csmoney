from time import time
from typing import Sequence

from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent

from proxy_http.aiohttp_session_factory import AiohttpSessionFactory
from proxy_http.async_proxies_concurrent_limiter import AsyncSessionConcurrentLimiter
from proxy_http.proxy import Proxy


user_agent_rotator = UserAgent(
    software_names=[SoftwareName.CHROME.value],
    operating_systems=[OperatingSystem.WINDOWS.value],
    limit=1000,
)


def _create_headers():
    return {
        "User-Agent": user_agent_rotator.get_random_user_agent(),
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        # 'X-Requested-With': 'XMLHttpRequest',
        "Connection": "keep-alive",
        # 'Referer': referer,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }


def create_limiter(proxies: Sequence[Proxy]):
    return AsyncSessionConcurrentLimiter(
        [
            AiohttpSessionFactory.create_session_with_proxy(proxy, headers=_create_headers())
            for proxy in proxies
        ],
        time(),
    )

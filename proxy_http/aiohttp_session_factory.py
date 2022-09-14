from typing import Optional, Mapping

from aiohttp import ClientSession

from proxy_http.aiohttp_addons.aihttp_socks_connector import ProxyConnector
from proxy_http.proxy import Proxy


class AiohttpSessionFactory:
    @staticmethod
    def create_session() -> ClientSession:
        return ClientSession()

    @staticmethod
    def create_session_with_proxy(
        proxy: Proxy, headers: Optional[Mapping[str, str]] = None
    ) -> ClientSession:
        connector = ProxyConnector.from_url(proxy.serialize(), ssl=False)
        return ClientSession(connector=connector, headers=headers)

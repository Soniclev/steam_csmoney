from abc import ABC, abstractmethod

from proxy_http.proxy import Proxy


class AbstractProxyStorage(ABC):
    @abstractmethod
    async def add(self, proxy: Proxy) -> None:
        ...

    @abstractmethod
    async def get_all(self) -> list[Proxy]:
        ...

    @abstractmethod
    async def remove(self, proxy: Proxy) -> None:
        ...

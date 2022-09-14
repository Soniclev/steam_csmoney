from aiohttp import TCPConnector

from python_socks import ProxyType, parse_proxy_url
from python_socks.async_.asyncio.v2 import Proxy


class ProxyConnector(TCPConnector):
    def __init__(
        self,
        proxy_type=ProxyType.SOCKS5,
        host=None,
        port=None,
        username=None,
        password=None,
        rdns=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._proxy_type = proxy_type
        self._proxy_host = host
        self._proxy_port = port
        self._proxy_username = username
        self._proxy_password = password
        self._rdns = rdns

    # noinspection PyMethodOverriding
    async def _wrap_create_connection(self, protocol_factory, host, port, *, ssl, **kwargs):
        proxy = Proxy.create(
            proxy_type=self._proxy_type,
            host=self._proxy_host,
            port=self._proxy_port,
            username=self._proxy_username,
            password=self._proxy_password,
            rdns=self._rdns,
            loop=self._loop,
        )

        connect_timeout = None

        timeout = kwargs.get("timeout")
        if timeout is not None:
            connect_timeout = getattr(timeout, "sock_connect", None)

        stream = await proxy.connect(
            dest_host=host, dest_port=port, dest_ssl=ssl, timeout=connect_timeout
        )

        transport = stream.writer.transport
        protocol = protocol_factory()

        transport.set_protocol(protocol)
        protocol.transport = transport

        return transport, protocol

    @classmethod
    def from_url(cls, url, **kwargs):
        proxy_type, host, port, username, password = parse_proxy_url(url)
        return cls(
            proxy_type=proxy_type,
            host=host,
            port=port,
            username=username,
            password=password,
            **kwargs,
        )

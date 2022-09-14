import urllib
from dataclasses import dataclass
from typing import Optional

from marshmallow_dataclass import add_schema

from common.core.dataclass_json import JsonMixin


@add_schema
@dataclass
class Proxy(JsonMixin):
    class Meta:
        ordered = True

    host: Optional[str] = None
    port: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    protocol: Optional[str] = None

    def __init__(
        self,
        proxy: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None,
        protocol: Optional[str] = None,
    ):
        if proxy:
            self.deserialize(proxy)
        else:
            self.host = host
            self.port = port
            self.login = login
            self.password = password
            self.protocol = protocol

    def get_identifier(self) -> str:
        return "{}:{}".format(self.host, self.port)

    def _build_proxy_url(self):
        url = ""
        if self.login and self.password:
            url += "{}:{}@".format(self.login, self.password)
        url += "{}:{}".format(self.host, self.port)
        return url

    def deserialize(self, s: str) -> bool:
        try:
            if "//" not in s:
                s = "//" + s
            result = urllib.parse.urlsplit(s)
            self.protocol = result.scheme
            if self.protocol == "https":
                self.protocol = "http"
            self.host = result.hostname
            self.port = str(result.port)
            self.login = result.username
            self.password = result.password
            return True
        except:
            self.protocol = None
            self.host = None
            self.port = None
            self.login = None
            self.password = None
            return False

    def serialize(self):
        return "{}://{}".format(self.protocol, self._build_proxy_url())

    def __eq__(self, other):
        if not isinstance(other, Proxy):
            return False
        return (
            self.host == other.host
            and self.port == other.port
            and self.login == other.login
            and self.password == other.password
        )

    def __repr__(self):
        return f"{self.host}:{self.port}"

    def __str__(self):
        return "{}://{}".format(self.protocol, self._build_proxy_url())

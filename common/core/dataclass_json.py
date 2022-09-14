from typing import Dict
import orjson


# noinspection PyUnresolvedReferences
class JsonMixin:
    @classmethod
    def load(cls, d: Dict):
        return cls.Schema().load(d)

    @classmethod
    def loads(cls, s: str):
        return cls.Schema().loads(s)

    @classmethod
    def load_bytes(cls, b: bytes):
        return cls.Schema().loads(b.decode())

    def dump(self) -> Dict:
        return self.Schema().dump(self)

    def dumps(self) -> str:
        return self.Schema().dumps(self)

    def dump_bytes(self) -> bytes:
        return self.Schema().dumps(self).encode()


# noinspection PyUnresolvedReferences
class FastJsonMixin:
    """This mixin does not support nested fields"""
    @classmethod
    def load(cls, d: Dict):
        return cls(**d)

    @classmethod
    def loads(cls, s: str):
        return cls(**orjson.loads(s))

    @classmethod
    def load_bytes(cls, b: bytes):
        return cls(**orjson.loads(b))

    def dump(self) -> Dict:
        return self.Schema().dump(self)

    def dumps(self) -> str:
        return self.Schema().dumps(self)

    def dump_bytes(self) -> bytes:
        return self.Schema().dumps(self).encode()

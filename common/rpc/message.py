from dataclasses import dataclass

from marshmallow_dataclass import add_schema

from ..core.dataclass_json import JsonMixin


@add_schema
@dataclass
class Message(JsonMixin):
    type_: str
    body: str

    def get_body(self, cls):
        return cls.load_bytes(self.body)

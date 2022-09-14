from unittest.mock import AsyncMock

import pytest


class MessageStub:
    def __init__(self, args: str):
        self._args = args
        self.reply = AsyncMock()

    def get_args(self):
        return self._args


@pytest.fixture()
def message():
    return MessageStub("")

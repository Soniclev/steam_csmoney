from typing import List
from unittest.mock import patch, AsyncMock, Mock

import pytest
from aiogram import types
from aiogram.types import ParseMode

from price_monitoring.telegram.bot.abstract_command import AbstractCommand
from price_monitoring.telegram.bot.abstract_whitelist import AbstractWhitelist
from price_monitoring.telegram.bot.aiogram_bot import AiogramBot
from price_monitoring.telegram.bot.notification_formatter import to_markdown
from price_monitoring.telegram.models import ItemOfferNotification

ALLOWED_MEMBERS = [1, 2, 3]

TEST_COMMAND = "test"


class CommandStub(AbstractCommand):
    def __init__(self):
        super(CommandStub, self).__init__(TEST_COMMAND)

    async def handler(self, message: types.Message):
        pass


class WhitelistStub(AbstractWhitelist):
    async def add_member(self, member: int) -> None:
        pass

    async def remove_member(self, member: int) -> None:
        pass

    async def get_members(self) -> List[int]:
        return ALLOWED_MEMBERS


class BotStub:
    def __init__(self, *args, **kwargs):
        self.send_message = AsyncMock()


class DispatcherStub:
    def __init__(self, *args, **kwargs):
        self.start_polling = AsyncMock()
        self.message_handler = Mock()


@pytest.fixture()
def command():
    return CommandStub()


@pytest.fixture()
def bot():
    with patch("aiogram.Bot", new=BotStub) as mock:
        yield mock


@pytest.fixture()
def dispatcher():
    with patch("aiogram.Dispatcher", new=DispatcherStub) as mock:
        yield mock


@pytest.fixture()
def whitelist():
    return WhitelistStub()


@pytest.fixture()
def aiogram_bot(whitelist, command, bot, dispatcher):
    return AiogramBot(token="token", whitelist=whitelist, commands=[command])


async def test_start(aiogram_bot):
    await aiogram_bot.start()

    aiogram_bot._dispatcher.message_handler.assert_called_with(
        commands=[TEST_COMMAND], user_id=ALLOWED_MEMBERS
    )
    aiogram_bot._dispatcher.start_polling.assert_called()


async def test_notify(aiogram_bot):
    notification = ItemOfferNotification(
        market_name="AK", orig_price=100, sell_price=90, short_title="UNKNOWN"
    )

    await aiogram_bot.notify(notification)

    assert aiogram_bot._bot.send_message.call_count == len(ALLOWED_MEMBERS)
    for call in aiogram_bot._bot.send_message.await_args_list:
        kwargs = call.kwargs
        assert kwargs["chat_id"] in ALLOWED_MEMBERS
        assert kwargs["text"] == to_markdown(notification)
        assert kwargs["parse_mode"] == ParseMode.MARKDOWN_V2
        assert kwargs["disable_web_page_preview"]

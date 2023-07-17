from unittest.mock import AsyncMock

import pytest

from price_monitoring.telegram.bot.commands.set_limit import SetLimit
from price_monitoring.telegram.models import NotificationSettings
from tests.telegram.bot.commands.conftest import MessageStub


@pytest.fixture()
def settings_provider():
    return AsyncMock()


@pytest.fixture()
def command(settings_provider):
    return SetLimit(settings_provider)


@pytest.mark.parametrize("text", ["15.3", "0", "-1.2", "-12.34", "1"])
async def test__limit_updated(settings_provider, command, text):
    settings_provider.get.return_value = NotificationSettings()
    percentage = float(text)
    message = MessageStub(text)

    await command.handler(message)

    settings = settings_provider.set.call_args[0][0]
    assert settings.max_threshold == percentage
    message.reply.assert_awaited_with(f"Limit for {percentage}% successfully set!")


@pytest.mark.parametrize("text", ["-15,3", "--15", "abc", "", "15.3%"])
async def test__failed_to_parse_args(settings_provider, command, text):
    message = MessageStub(text)

    await command.handler(message)

    message.reply.assert_awaited_with(f"could not convert string to float: '{text}'")


async def test__reply_with_error(settings_provider, command):
    message = MessageStub("15.3")
    settings_provider.get.side_effect = ValueError("Some error!")

    await command.handler(message)

    message.reply.assert_awaited_with("Some error!")


async def test__settings_not_loaded(settings_provider, command):
    message = MessageStub("15.3")
    settings_provider.get.return_value = None

    await command.handler(message)

    message.reply.assert_awaited_with("Failed to load settings!")

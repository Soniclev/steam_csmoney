from unittest.mock import AsyncMock

import pytest

from price_monitoring.telegram.bot.commands.settings import Settings
from price_monitoring.telegram.models import NotificationSettings


@pytest.fixture()
def settings_provider():
    return AsyncMock()


@pytest.fixture()
def command(settings_provider):
    return Settings(settings_provider)


async def test__offer_provider_call(settings_provider, command, message):
    settings = NotificationSettings()
    settings_provider.get.return_value = settings

    await command.handler(message)

    message.reply.assert_awaited_with(f"Current settings: {str(settings)}")


async def test__reply_with_error(settings_provider, command, message):
    settings_provider.get.side_effect = ValueError("There is an error!")

    await command.handler(message)

    message.reply.assert_awaited_with("There is an error!")

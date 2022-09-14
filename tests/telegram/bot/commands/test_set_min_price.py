from unittest.mock import AsyncMock

import pytest

from price_monitoring.telegram.bot.commands.set_min_price import SetMinPrice
from price_monitoring.telegram.models import NotificationSettings
from tests.telegram.bot.commands.conftest import MessageStub


@pytest.fixture()
def settings_provider():
    return AsyncMock()


@pytest.fixture()
def command(settings_provider):
    return SetMinPrice(settings_provider)


@pytest.mark.parametrize("text", ["15.3", "0", "1", "12.34"])
async def test__min_price_updated(settings_provider, command, text):
    settings_provider.get.return_value = NotificationSettings()
    min_price = float(text)
    message = MessageStub(text)

    await command.handler(message)

    settings = settings_provider.set.call_args[0][0]
    assert settings.min_price == min_price
    message.reply.assert_awaited_with(f"Минимальная цена в ${min_price} успешно установлена!")


@pytest.mark.parametrize("text", ["15,3", "--15", "abc", "", "$15.3"])
async def test__failed_to_parse_args(settings_provider, command, text):
    message = MessageStub(text)

    await command.handler(message)

    assert settings_provider.set.call_count == 0
    message.reply.assert_awaited_with(f"could not convert string to float: '{text}'")


async def test__negative_value_not_allowed(settings_provider, command):
    message = MessageStub("-2.34")

    await command.handler(message)

    assert settings_provider.set.call_count == 0
    message.reply.assert_awaited_with(f"Отрицательные значения не допустимы!")


async def test__reply_with_error(settings_provider, command):
    message = MessageStub("15.3")
    settings_provider.get.side_effect = ValueError("Some error!")

    await command.handler(message)

    assert settings_provider.set.call_count == 0
    message.reply.assert_awaited_with("Some error!")


async def test__settings_not_loaded(settings_provider, command):
    message = MessageStub("15.3")
    settings_provider.get.return_value = None

    await command.handler(message)

    message.reply.assert_awaited_with("Не удалось загрузить настройки!")

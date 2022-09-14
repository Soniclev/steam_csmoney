from unittest.mock import AsyncMock

import pytest

from price_monitoring.telegram.models import NotificationSettings
from price_monitoring.telegram.offer_provider.settings_based_provider import SettingsBasedProvider


@pytest.fixture()
def settings_provider():
    return AsyncMock()


@pytest.fixture()
def offer_provider():
    return AsyncMock()


@pytest.fixture()
def main_provider(settings_provider, offer_provider):
    return SettingsBasedProvider(settings_provider, offer_provider)


@pytest.mark.parametrize("percentage_limit", [None, -10])
@pytest.mark.parametrize("min_price", [None, 20])
async def test__offer_provider_call(
    settings_provider, offer_provider, main_provider, percentage_limit, min_price
):
    settings = NotificationSettings(min_price=15.12, max_threshold=-12.34)
    settings_provider.get.return_value = settings
    offer_provider.get_items.return_value = [1, 2]

    result = await main_provider.get_items(percentage_limit=percentage_limit, min_price=min_price)

    assert result == [1, 2]
    expected_percentage_limit = percentage_limit or settings.max_threshold
    expected_min_price = min_price or settings.min_price
    offer_provider.get_items.assert_awaited_with(
        percentage_limit=expected_percentage_limit, min_price=expected_min_price
    )


async def test_no_settings(settings_provider, main_provider):
    settings_provider.get.return_value = None

    with pytest.raises(ValueError, match="Failed to load settings!"):
        await main_provider.get_items()

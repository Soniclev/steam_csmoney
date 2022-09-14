import os

from common.tracer import setup_decorator
from common.redis_connector import RedisConnector
from price_monitoring.async_runner import async_run
from price_monitoring.constants import TelegramRedisKeys, RedisKeys
from price_monitoring.storage.csmoney import RedisCsmoneyItemStorage
from price_monitoring.storage.steam import RedisSteamOrdersStorage, RedisSteamSellHistoryStorage
from price_monitoring.telegram.bot import AiogramBot, RedisSettings, RedisWhitelist
from price_monitoring.telegram.bot.commands import Offers, SetLimit, SetMinPrice, Settings
from price_monitoring.telegram.fresh_filter import RedisFilter
from price_monitoring.telegram.offer_provider import (
    ChainProvider,
    RedisOfferProvider,
    RedisSellHistoryProvider,
    SettingsBasedProvider,
)
from price_monitoring.telegram.runner import Runner

worker_redis_credentials = {
    "host": os.getenv("WORKER_REDIS_HOST"),
    "port": os.getenv("WORKER_REDIS_PORT"),
    "db": os.getenv("WORKER_REDIS_DB"),
    "password": os.getenv("WORKER_REDIS_PASSWORD"),
}

cache_redis_credentials = {
    "host": os.getenv("CACHE_REDIS_HOST"),
    "port": os.getenv("CACHE_REDIS_PORT"),
    "db": os.getenv("CACHE_REDIS_DB"),
    "password": os.getenv("CACHE_REDIS_PASSWORD"),
}

telegram_redis_credentials = {
    "host": os.getenv("TELEGRAM_REDIS_HOST"),
    "port": os.getenv("TELEGRAM_REDIS_PORT"),
    "db": os.getenv("TELEGRAM_REDIS_DB"),
    "password": os.getenv("TELEGRAM_REDIS_PASSWORD"),
}


async def _fill_whitelist(whitelist):
    members = os.getenv("TELEGRAM_WHITELIST")
    if members:
        for member in members.split(","):
            await whitelist.add_member(int(member))


@setup_decorator("http://127.0.0.1:9411/api/v2/spans", "tg_bot")
async def main():
    telegram_api_token = os.getenv("TELEGRAM_API_TOKEN")

    worker_redis = RedisConnector.create(**worker_redis_credentials)
    cache_redis = RedisConnector.create(**cache_redis_credentials)
    telegram_redis = RedisConnector.create(**telegram_redis_credentials)
    whitelist = RedisWhitelist(telegram_redis, TelegramRedisKeys.WHITELIST_KEY)
    await _fill_whitelist(whitelist)
    settings = RedisSettings(telegram_redis, TelegramRedisKeys.SETTINGS_KEY)
    await settings.set_default()
    settings_based_provider = SettingsBasedProvider(
        settings,
        RedisOfferProvider(
            RedisSteamOrdersStorage(worker_redis),
            RedisCsmoneyItemStorage(worker_redis, RedisKeys.CSMONEY_UNLOCKED_ITEMS, False),
        ),
    )
    settings_based_provider_sell_history = SettingsBasedProvider(
        settings,
        ChainProvider(
            [
                RedisSellHistoryProvider(
                    RedisSteamSellHistoryStorage(worker_redis),
                    RedisCsmoneyItemStorage(worker_redis, RedisKeys.CSMONEY_UNLOCKED_ITEMS, False),
                ),
                RedisSellHistoryProvider(
                    RedisSteamSellHistoryStorage(worker_redis),
                    RedisCsmoneyItemStorage(worker_redis, RedisKeys.CSMONEY_LOCKED_ITEMS, True),
                ),
            ]
        ),
    )
    chain_provider = ChainProvider([settings_based_provider, settings_based_provider_sell_history])
    bot = AiogramBot(
        telegram_api_token,
        whitelist,
        [
            SetLimit(settings),
            Settings(settings),
            SetMinPrice(settings),
            Offers(chain_provider),
        ],
    )
    await bot.start()
    runner = Runner(bot=bot, price_provider=chain_provider, filter_=RedisFilter(cache_redis))
    await runner.run()


if __name__ == "__main__":
    async_run(main())

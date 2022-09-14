import asyncio
import datetime
import os

from common.rabbitmq_connector import RabbitmqConnector
from common.redis_connector import RedisConnector
from common.rpc.queue_factory import QueueFactory
from price_monitoring.async_runner import async_run
from price_monitoring.common import create_limiter
from price_monitoring.constants import QueueNames, RedisKeys
from price_monitoring.parsers.steam import SteamOrderParser
from price_monitoring.parsers.steam import SteamSellHistoryParser
from price_monitoring.parsers.steam.name_resolver import (
    RedisCachedNameResolver,
    MemoryCachedNameResolver,
    NameResolver,
)
from price_monitoring.parsers.steam.parser import (
    SteamOrdersParser,
    SteamSellHistoryParser as SteamSellHistoryParserImpl,
)
from price_monitoring.parsers.steam.skin_scheduler import RedisSkinScheduler
from price_monitoring.parsers.steam.skin_scheduler import SchedulerFiller
from price_monitoring.queues.rabbitmq import MarketNameReader
from price_monitoring.queues.rabbitmq import SteamOrderWriter
from price_monitoring.queues.rabbitmq import SteamSellHistoryWriter
from price_monitoring.storage.proxy import RedisProxyStorage

redis_credentials = {
    "host": os.getenv("REDIS_HOST"),
    "port": os.getenv("REDIS_PORT"),
    "db": os.getenv("REDIS_DB"),
    "password": os.getenv("REDIS_PASSWORD"),
}

rabbitmq_credentials = {
    "host": os.getenv("RABBITMQ_HOST"),
    "port": os.getenv("RABBITMQ_PORT"),
    "login": os.getenv("RABBITMQ_LOGIN"),
    "password": os.getenv("RABBITMQ_PASSWORD"),
}

ORDER_WORKERS_COUNT = int(os.getenv("ORDER_WORKERS_COUNT", "1"))
SELL_HISTORY_WORKERS_COUNT = int(os.getenv("SELL_HISTORY_WORKERS_COUNT", "1"))
SELL_HISTORY_LOCK_DURATION = datetime.timedelta(seconds=60)
SELL_HISTORY_POSTPONE = datetime.timedelta(hours=6)


async def main():
    redis = RedisConnector.create(**redis_credentials)
    rabbitmq = await RabbitmqConnector.connect(**rabbitmq_credentials)

    market_name_queue_reader = MarketNameReader(
        await QueueFactory.connect_reader(QueueNames.STEAM_MARKET_NAME, rabbitmq)
    )
    steam_result_queue = SteamOrderWriter(
        await QueueFactory.connect_publisher(QueueNames.STEAM_RESULT, rabbitmq)
    )
    steam_history_queue = SteamSellHistoryWriter(
        await QueueFactory.connect_publisher(QueueNames.STEAM_SELL_HISTORY_RESULT, rabbitmq)
    )

    skin_order_scheduler = RedisSkinScheduler(redis, key=RedisKeys.STEAM_SKIN_SCHEDULE)
    skin_history_scheduler = RedisSkinScheduler(
        redis,
        key=RedisKeys.STEAM_SKIN_HISTORY_SCHEDULE,
        postpone=SELL_HISTORY_POSTPONE,
        lock_duration=SELL_HISTORY_LOCK_DURATION,
    )

    storage = RedisProxyStorage(redis, key=RedisKeys.STEAM_PROXIES)
    proxies = await storage.get_all()

    steam_limiter = create_limiter(proxies)

    name_resolver = MemoryCachedNameResolver(
        RedisCachedNameResolver(resolver=NameResolver(steam_limiter), redis=redis)
    )

    scheduler_filler = SchedulerFiller(
        market_name_queue=market_name_queue_reader,
        skin_schedulers=[skin_order_scheduler, skin_history_scheduler],
    )
    asyncio.create_task(scheduler_filler.run())

    tasks = [
        SteamOrderParser(
            parser=SteamOrdersParser(steam_limiter, name_resolver),
            skin_scheduler=skin_order_scheduler,
            steam_result_queue=steam_result_queue,
        ).run()
        for _ in range(ORDER_WORKERS_COUNT)
    ]
    tasks.extend(
        [
            SteamSellHistoryParser(
                parser=SteamSellHistoryParserImpl(limiter=steam_limiter),
                skin_scheduler=skin_history_scheduler,
                result_queue=steam_history_queue,
            ).run()
            for _ in range(SELL_HISTORY_WORKERS_COUNT)
        ]
    )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    async_run(main())

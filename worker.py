import asyncio
import os

from common.rabbitmq_connector import RabbitmqConnector
from common.redis_connector import RedisConnector
from common.rpc.queue_factory import QueueFactory
from price_monitoring.async_runner import async_run
from price_monitoring.constants import QueueNames, RedisKeys
from price_monitoring.features.overpay.storage import RedisOverpayStorage
from price_monitoring.features.overpay.worker import OverpayExtractor
from price_monitoring.queues.rabbitmq import CsmoneyReader
from price_monitoring.queues.rabbitmq import SteamSellHistoryReader
from price_monitoring.queues.rabbitmq.market_name_queue import MarketNameWriter
from price_monitoring.queues.rabbitmq.steam_result_queue import SteamOrderReader
from price_monitoring.storage.csmoney import RedisCsmoneyItemStorage
from price_monitoring.storage.steam import RedisSteamOrdersStorage, RedisSteamSellHistoryStorage
from price_monitoring.worker.processing import (
    SteamSellHistoryProcessor,
    SteamSkinProcessor,
    CsmoneyItemProcessor,
    MarketNameExtractor,
)
from price_monitoring.worker.worker import Worker, WorkerThread

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

WORKERS_COUNT = int(os.getenv("WORKERS_COUNT", "1"))


async def main():
    redis = RedisConnector.create(**redis_credentials)
    rabbitmq = await RabbitmqConnector.connect(**rabbitmq_credentials)

    csmoney_result_queue_reader = CsmoneyReader(
        await QueueFactory.connect_reader(QueueNames.CSMONEY_RESULT, rabbitmq)
    )
    market_name_queue_writer = MarketNameWriter(
        await QueueFactory.connect_publisher(QueueNames.STEAM_MARKET_NAME, rabbitmq)
    )
    steam_result_queue_reader = SteamOrderReader(
        await QueueFactory.connect_reader(QueueNames.STEAM_RESULT, rabbitmq)
    )
    steam_sell_history_queue_reader = SteamSellHistoryReader(
        await QueueFactory.connect_reader(QueueNames.STEAM_SELL_HISTORY_RESULT, rabbitmq)
    )

    csmoney_processor = CsmoneyItemProcessor(
        unlocked_storage=RedisCsmoneyItemStorage(redis, RedisKeys.CSMONEY_UNLOCKED_ITEMS, False),
        locked_storage=RedisCsmoneyItemStorage(redis, RedisKeys.CSMONEY_LOCKED_ITEMS, True),
    )
    market_name_extractor = MarketNameExtractor(market_name_queue=market_name_queue_writer)

    steam_processor = SteamSkinProcessor(RedisSteamOrdersStorage(redis))
    steam_sell_history_processor = SteamSellHistoryProcessor(RedisSteamSellHistoryStorage(redis))
    overpay_extractor = OverpayExtractor(RedisOverpayStorage(redis))

    await asyncio.gather(
        *[
            Worker(
                threads=[
                    WorkerThread(
                        reader=csmoney_result_queue_reader,
                        delay_duration=0.5,
                        processors=[
                            csmoney_processor,
                            market_name_extractor,
                            overpay_extractor,
                        ],
                    ),
                    WorkerThread(
                        reader=steam_result_queue_reader,
                        delay_duration=0.5,
                        processors=[steam_processor],
                    ),
                    WorkerThread(
                        reader=steam_sell_history_queue_reader,
                        delay_duration=1,
                        processors=[steam_sell_history_processor],
                    ),
                ]
            ).run()
            for _ in range(WORKERS_COUNT)
        ]
    )


if __name__ == "__main__":
    async_run(main())

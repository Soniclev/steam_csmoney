import os

from common.rabbitmq_connector import RabbitmqConnector
from common.redis_connector import RedisConnector
from common.rpc.queue_factory import QueueFactory
from price_monitoring.async_runner import async_run
from price_monitoring.common import create_limiter
from price_monitoring.constants import QueueNames, RedisKeys
from price_monitoring.parsers.csmoney import CsmoneyParser
from price_monitoring.parsers.csmoney.parser import CsmoneyParserImpl
from price_monitoring.parsers.csmoney.task_scheduler import RedisTaskScheduler
from price_monitoring.queues.rabbitmq import CsmoneyWriter
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


async def main():
    redis = RedisConnector.create(**redis_credentials)
    rabbitmq = await RabbitmqConnector.connect(**rabbitmq_credentials)

    csmoney_result_queue = CsmoneyWriter(
        await QueueFactory.connect_publisher(QueueNames.CSMONEY_RESULT, rabbitmq)
    )

    storage = RedisProxyStorage(redis, RedisKeys.STEAM_PROXIES)
    proxies = await storage.get_all()

    csmoney_limiter = create_limiter(proxies)

    parser = CsmoneyParser(
        impl=CsmoneyParserImpl(csmoney_limiter),
        result_queue=csmoney_result_queue,
        task_scheduler=RedisTaskScheduler(redis),
    )

    await parser.run()


if __name__ == "__main__":
    async_run(main())

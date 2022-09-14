import asyncio

from common.env_var import EnvVar
from common.redis_connector import RedisConnector
from price_monitoring.models.csmoney import CsmoneyTask
from price_monitoring.parsers.csmoney.task_scheduler import RedisTaskScheduler


def generate_tasks() -> list[CsmoneyTask]:
    fmt = (
        "https://inventories.cs.money/5.0/load_bots_inventory/730?hasTradeLock=false"
        "&hasTradeLock=true&isMarket=false&limit=60&maxPrice={max_price}&minPrice={min_price}"
        "&withStack=true"
    )

    result = []
    value = 0.2
    step = 0.1

    while value < 500:
        new_value = round(value + step, 2)
        step = value
        url = fmt.format(min_price=value, max_price=new_value)
        result.append(CsmoneyTask(url=url))
        value = new_value
    return result


async def main():
    redis = RedisConnector.create(
        host=EnvVar.get("REDIS_HOST"),
        port=EnvVar.get("REDIS_PORT"),
        db=EnvVar.get("REDIS_DB"),
        password=EnvVar.get("REDIS_PASSWORD"),
    )
    scheduler = RedisTaskScheduler(redis)
    await scheduler.clear()
    tasks = generate_tasks()
    print(f"Generated {len(tasks)} tasks.")
    for task in tasks:
        await scheduler.append_task(task)


if __name__ == "__main__":
    asyncio.run(main())

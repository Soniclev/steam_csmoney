import datetime
import hashlib

from aioredis import Redis

from ....models.csmoney import CsmoneyTask

_SET_KEY = "csmoney_task_schedule"
_POSTPONE = datetime.timedelta(minutes=2)
_LOCK_DURATION = datetime.timedelta(seconds=120)


def _lock_key(market_name: str) -> str:
    return f"csmoney_task_lock:{hashlib.sha256(market_name.encode()).hexdigest()}"


class RenewFailedError(Exception):
    pass


class RedisTaskScheduler:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def append_task(self, task: CsmoneyTask) -> None:
        unixtime = datetime.datetime.now().timestamp()
        await self._redis.zadd(name=_SET_KEY, mapping={task.dumps(): unixtime}, nx=True)

    async def delete_task(self, task: CsmoneyTask) -> None:
        await self._redis.zrem(_SET_KEY, task.dumps())

    async def clear(self) -> None:
        await self._redis.delete(_SET_KEY)

    async def get_task(self) -> CsmoneyTask | None:
        unixtime = datetime.datetime.now().timestamp()
        tasks = await self._redis.zrangebyscore(
            name=_SET_KEY, min="-inf", max=unixtime, start=0, num=10
        )  # 10 is enough
        for task in tasks:
            task = task.decode()
            is_success = await self._redis.set(
                name=_lock_key(task), nx=True, ex=_LOCK_DURATION, value=1
            )
            if is_success:
                return CsmoneyTask.loads(task)
        return None

    async def renew_task_lock(self, task: CsmoneyTask) -> None:
        if not await self._redis.set(
            name=_lock_key(task.dumps()), xx=True, ex=_LOCK_DURATION, value=1
        ):
            raise RenewFailedError()

    async def release_task(self, task: CsmoneyTask, is_success: bool) -> None:
        data = task.dumps()
        if is_success:
            unixtime = (datetime.datetime.now() + _POSTPONE).timestamp()
            await self._redis.zadd(name=_SET_KEY, mapping={data: unixtime}, xx=True)
        await self._redis.delete(_lock_key(data))

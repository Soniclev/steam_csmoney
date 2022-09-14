import datetime

from aioredis import Redis

from .abstract_skin_scheduler import AbstractSkinScheduler
from ....types import MarketName


def _lock_key(market_name: MarketName) -> str:
    return f"steam_skin_lock:{market_name}"


class RedisSkinScheduler(AbstractSkinScheduler):
    def __init__(
        self,
        redis: Redis,
        key: str,
        postpone: datetime.timedelta = datetime.timedelta(minutes=15),
        lock_duration: datetime.timedelta = datetime.timedelta(seconds=60),
    ):
        self._redis = redis
        self._key = key
        self._postpone = postpone
        self._lock_duration = lock_duration

    async def append_market_name(self, market_name: MarketName) -> None:
        unixtime = datetime.datetime.now().timestamp()
        await self._redis.zadd(name=self._key, mapping={market_name: unixtime}, nx=True)

    async def delete_skin(self, market_name: MarketName) -> None:
        await self._redis.zrem(self._key, market_name)

    async def get_skin(self) -> MarketName | None:
        unixtime = datetime.datetime.now().timestamp()
        market_names = await self._redis.zrangebyscore(
            name=self._key, min="-inf", max=unixtime, start=0, num=50
        )  # 50 is enough
        for market_name in market_names:
            market_name = market_name.decode()
            is_success = await self._redis.set(
                name=_lock_key(market_name), nx=True, ex=self._lock_duration, value=1
            )
            if is_success:
                return market_name
        return None

    async def release_skin(self, market_name: MarketName, is_success: bool) -> None:
        if is_success:
            unixtime = (datetime.datetime.now() + self._postpone).timestamp()
            await self._redis.zadd(name=self._key, mapping={market_name: unixtime}, xx=True)
        await self._redis.delete(_lock_key(market_name))

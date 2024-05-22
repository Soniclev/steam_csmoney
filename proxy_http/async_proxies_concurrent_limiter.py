import asyncio
from asyncio import Lock
from time import time
from typing import List

from aiohttp import ClientSession


class NoAvailableSessionError(Exception):
    pass


class AsyncSessionConcurrentLimiter:
    def __init__(self, sessions: List[ClientSession], timestamp: float):
        self._sessions = {session: timestamp for session in sessions}
        self._lock = Lock()

    async def get_available(self, postpone_duration: float) -> ClientSession:
        while True:
            try:
                async with self._lock:
                    return self._get_available_no_wait(time(), postpone_duration)
            except NoAvailableSessionError:
                await asyncio.sleep(0.1)

    def _get_available_no_wait(self, timestamp: float, postpone_duration: float) -> ClientSession:
        for session in self._sessions:
            if timestamp > self._sessions[session]:
                self._postpone(session, timestamp + postpone_duration)
                return session
        raise NoAvailableSessionError

    def _postpone(self, session: ClientSession, timestamp: float):
        try:
            self._sessions[session] = timestamp
        except KeyError:
            raise NoAvailableSessionError

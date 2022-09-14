import asyncio

try:
    from asyncio import WindowsSelectorEventLoopPolicy
except ImportError:
    WindowsSelectorEventLoopPolicy = None  # linux version of Python doesn't contain this policy
import platform
from typing import Any, Coroutine

try:
    import uvloop
except ImportError:
    uvloop = None  # uvloop doesn't support Windows


def async_run(func: Coroutine[Any, Any, Any]):
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    else:
        # noinspection PyUnresolvedReferences
        uvloop.install()
    asyncio.run(func)

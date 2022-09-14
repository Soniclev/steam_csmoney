import asyncio
import logging
import timeit
from functools import wraps

_INFINITE_RUN = True  # used in unit-tests


def async_infinite_loop(logger: logging.Logger):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await _cycle(args, kwargs)
            while _INFINITE_RUN:  # pragma: no cover
                await _cycle(args, kwargs)

        async def _cycle(args, kwargs):
            try:
                await func(*args, **kwargs)
            except Exception as exc:
                logger.exception(exc)
            await asyncio.sleep(0)

        return wrapper

    return decorator


def timer(logger: logging.Logger, level: int = logging.INFO):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = timeit.default_timer()
            result = await func(*args, **kwargs)
            elapsed = round(timeit.default_timer() - start_time, 3)
            logger.log(level, f'Function "{func.__name__}" took {elapsed} seconds to complete.')
            return result

        return wrapper

    return decorator

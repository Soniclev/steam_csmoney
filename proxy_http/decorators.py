import asyncio
from functools import wraps

import aiohttp


def catch_aiohttp(logger):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (aiohttp.ClientHttpProxyError, aiohttp.ClientProxyConnectionError) as exc:
                logger.exception("Failed to connect to proxy", exc_info=exc)
            except (
                asyncio.exceptions.TimeoutError,
                aiohttp.ClientConnectionError,
                aiohttp.ClientPayloadError,
                aiohttp.ClientResponseError,
                ConnectionResetError,
            ) as exc:
                logger.exception("Failed to connect to proxy", exc_info=exc)

        return wrapper

    return decorator

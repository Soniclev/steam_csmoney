import pytest


@pytest.fixture(autouse=True)
def no_asyncio_sleep(disable_asyncio_sleep):
    ...

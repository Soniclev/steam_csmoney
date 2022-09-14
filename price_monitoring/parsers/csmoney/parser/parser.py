import logging
from datetime import datetime

from aiohttp import ClientSession

from proxy_http.async_proxies_concurrent_limiter import AsyncSessionConcurrentLimiter
from proxy_http.decorators import catch_aiohttp
from .abstract_parser import MaxAttemptsReachedError, AbstractCsmoneyParser
from ._name_patcher import patch_market_name
from ....models.csmoney import CsmoneyItem, CsmoneyItemPack, CsmoneyItemCategory
from ....queues import AbstractCsmoneyWriter

# currently, it cannot be greater than 60
# because cs.money server side don't allow greater value
_MAX_ALLOWED_OFFSET = 5000
_CSMONEY_STEP = 60
_RESPONSE_TIMEOUT = 10
_POSTPONE_DURATION = 15

logger = logging.getLogger(__name__)


def _csmoney_unix_to_datetime(unix: int | None) -> datetime | None:
    if unix:
        return datetime.utcfromtimestamp(unix / 1000)
    return None


def _append_offset(url: str, offset: int) -> str:
    return f"{url}&offset={offset}"


def _is_response_mean_end(data: dict) -> bool:
    return data == {"error": 2}  # it marks end of items


def _create_items(json_item) -> list[CsmoneyItem]:
    if "fullName" not in json_item:
        return []
    name = patch_market_name(json_item["fullName"])
    overpay = json_item.get("overpay", None)
    overpay_float = overpay.get("float", None) if overpay else None
    items = [
        CsmoneyItem(
            name=name,
            price=json_item["price"],
            asset_id=str(json_item["assetId"]),
            name_id=json_item["nameId"],
            type_=CsmoneyItemCategory(json_item["type"]),
            float_=json_item.get("float", None),
            unlock_timestamp=_csmoney_unix_to_datetime(json_item.get("tradeLock", None)),
            overpay_float=overpay_float,
        )
    ]
    is_stack = "stackSize" in json_item and "stackId" in json_item and "stackItems" in json_item
    if is_stack:
        for stack_item in json_item["stackItems"]:
            items.append(
                CsmoneyItem(
                    name=name,
                    price=json_item["price"],
                    asset_id=str(stack_item["id"]),
                    name_id=json_item["nameId"],
                    type_=CsmoneyItemCategory(json_item["type"]),
                    float_=stack_item.get("float", None),
                    unlock_timestamp=_csmoney_unix_to_datetime(stack_item["tradeLock"]),
                    overpay_float=None,
                )
            )
    return items


@catch_aiohttp(logger)
async def _request(session: ClientSession, step_url: str) -> dict | None:
    async with session.get(step_url, timeout=_RESPONSE_TIMEOUT) as response:
        response.raise_for_status()
        return await response.json()


async def _process_json_data(data, result_queue: AbstractCsmoneyWriter) -> None:
    assert "items" in data
    pack = CsmoneyItemPack()
    for json_item in data["items"]:
        items = _create_items(json_item)
        for item in items:
            pack.items.append(item)
    await result_queue.put(pack)


class CsmoneyParserImpl(AbstractCsmoneyParser):
    def __init__(self, limiter: AsyncSessionConcurrentLimiter):
        self._limiter = limiter

    async def parse(
        self, url: str, result_queue: AbstractCsmoneyWriter, max_attempts: int = 10
    ) -> None:
        failed_attempts = 0
        offset = 0

        while failed_attempts <= max_attempts:
            if offset > _MAX_ALLOWED_OFFSET:
                logger.warning(f"Reached max allowed offset ({_MAX_ALLOWED_OFFSET})!")
                break
            step_url = _append_offset(url, offset)
            session = await self._limiter.get_available(_POSTPONE_DURATION)
            response = await _request(session, step_url)
            if not response:
                logger.info(
                    f"Failed on {failed_attempts} attempt to load {step_url=}",
                    extra={"attempt": failed_attempts, "url": step_url},
                )
                failed_attempts += 1
                continue
            offset += _CSMONEY_STEP

            logger.info(
                f"Successfully got a response for {step_url=}",
                extra={"response": response, "url": step_url},
            )

            if _is_response_mean_end(response):  # it marks end of items
                logger.info(f"Found end of items for {step_url=}")
                break
            await _process_json_data(response, result_queue)

        if failed_attempts > max_attempts:
            raise MaxAttemptsReachedError()

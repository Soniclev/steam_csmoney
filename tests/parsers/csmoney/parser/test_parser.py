import datetime
import json
from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from price_monitoring.models.csmoney import CsmoneyItem, CsmoneyItemPack, CsmoneyItemCategory
from price_monitoring.parsers.csmoney.parser.abstract_parser import MaxAttemptsReachedError
from price_monitoring.parsers.csmoney.parser.parser import (
    CsmoneyParserImpl,
    _is_response_mean_end,
    _append_offset,
    _csmoney_unix_to_datetime,
    _create_items,
)


@pytest.fixture()
async def limiter_fixture():
    session = ClientSession()
    m = AsyncMock()
    m.get_available.return_value = session
    yield m
    await session.close()


@pytest.fixture()
def result_queue_fixture():
    return AsyncMock()


@pytest.fixture()
def parser_fixture(limiter_fixture):
    return CsmoneyParserImpl(limiter_fixture)


@pytest.fixture()
def response_fixture():
    with open("tests/parsers/csmoney/parser/data/item_1.json", encoding="utf8") as f:
        return json.load(f)


@pytest.fixture()
def csmoney_item_fixture():
    return CsmoneyItem(
        name="★ Butterfly Knife | Doppler (Factory New)",
        price=24768.93,
        asset_id="24898849555",
        name_id=3985,
        type_=CsmoneyItemCategory.KNIFE,
        float_="0.008115612901747",
        unlock_timestamp=datetime.datetime.fromisoformat("2022-02-21T08:00:00"),
        overpay_float=140.69,
    )


@pytest.fixture()
def csmoney_item_pack_fixture(csmoney_item_fixture):
    return CsmoneyItemPack(items=[csmoney_item_fixture] * 60)


@pytest.fixture()
def csmoney_responses_fixture(response_fixture):
    items = {"items": [response_fixture for _ in range(60)]}
    empty = {"error": 2}
    with aioresponses() as m:
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=0",
            payload=items,
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=60",
            payload=items,
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=120",
            payload=items,
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=180",
            payload=empty,
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=240",
            payload=empty,
        )
        yield m


@pytest.fixture()
def csmoney_responses_with_errors_fixture(response_fixture):
    items = {"items": [response_fixture for _ in range(60)]}
    empty = {"error": 2}

    with aioresponses() as m:
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=0",
            payload=items,
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=60",
            exception=aiohttp.ClientProxyConnectionError(None, OSError()),
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=60",
            payload=items,
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=120",
            exception=aiohttp.ClientConnectionError(),
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=120",
            exception=ConnectionResetError(),
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=120",
            payload=items,
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=180",
            payload=empty,
        )
        m.get(
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=240",
            payload=empty,
        )
        yield m


@pytest.mark.parametrize(
    "data,end",
    [
        ({"error": 2}, True),
        ({"items": []}, False),
    ],
)
def test_is_response_mean_end(data: dict, end: bool):
    assert _is_response_mean_end(data) == end


def test_append_offset():
    url = _append_offset("https://cs.money/api?count=60", 21)
    assert url == "https://cs.money/api?count=60&offset=21"


def test_csmoney_unix_to_datetime():
    assert _csmoney_unix_to_datetime(1645009200000) == datetime.datetime.fromisoformat(
        "2022-02-16T11:00:00"
    )


def test_create_items_without_stack():
    with open("tests/parsers/csmoney/parser/data/item_1.json", encoding="utf8") as f:
        data = json.load(f)
        items = [
            CsmoneyItem(
                name="★ Butterfly Knife | Doppler (Factory New)",
                price=24768.93,
                asset_id="24898849555",
                name_id=3985,
                type_=CsmoneyItemCategory.KNIFE,
                float_="0.008115612901747",
                unlock_timestamp=datetime.datetime.fromisoformat("2022-02-21T08:00:00"),
                overpay_float=140.69,
            )
        ]
        assert _create_items(data) == items


def test_create_items_without_full_name():
    with open(
        "tests/parsers/csmoney/parser/data/item_without_full_name_1.json",
        encoding="utf8",
    ) as f:
        data = json.load(f)
        assert _create_items(data) == []


def test_create_items_with_stack():
    with open("tests/parsers/csmoney/parser/data/item_with_stack_1.json", encoding="utf8") as f:
        data = json.load(f)
        items = [
            CsmoneyItem(
                name="★ Sport Gloves | Vice (Factory New)",
                price=35718.7,
                asset_id="24491496626",
                name_id=29570,
                type_=CsmoneyItemCategory.GLOVE,
                float_="0.065496817231178",
                unlock_timestamp=None,
                overpay_float=None,
            ),
            CsmoneyItem(
                name="★ Sport Gloves | Vice (Factory New)",
                price=35718.7,
                asset_id="24571330159",
                name_id=29570,
                type_=CsmoneyItemCategory.GLOVE,
                float_="0.067453943192958",
                unlock_timestamp=None,
                overpay_float=None,
            ),
        ]
        assert _create_items(data) == items


def test_create_items_with_stack_and_tradelock():
    with open("tests/parsers/csmoney/parser/data/item_with_stack_2.json", encoding="utf8") as f:
        data = json.load(f)
        items = [
            CsmoneyItem(
                name="★ M9 Bayonet | Doppler (Factory New)",
                price=11592.8,
                asset_id="24899230485",
                name_id=15840,
                type_=CsmoneyItemCategory.KNIFE,
                float_="0.056123819202184",
                unlock_timestamp=datetime.datetime.fromisoformat("2022-02-21T08:00:00"),
                overpay_float=None,
            ),
            CsmoneyItem(
                name="★ M9 Bayonet | Doppler (Factory New)",
                price=11592.8,
                asset_id="24902572721",
                name_id=15840,
                type_=CsmoneyItemCategory.KNIFE,
                float_="0.06806051731109601",
                unlock_timestamp=datetime.datetime.fromisoformat("2022-02-21T08:00:00"),
                overpay_float=None,
            ),
        ]
        assert _create_items(data) == items


async def test_parse__assert_items(
    parser_fixture,
    result_queue_fixture,
    csmoney_responses_fixture,
    csmoney_item_pack_fixture,
):
    await parser_fixture.parse(
        "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true",
        result_queue_fixture,
    )

    assert result_queue_fixture.put.call_count == 3
    for call in result_queue_fixture.put.call_args_list:
        assert call.args == (csmoney_item_pack_fixture,)


async def test_parse__assert_requests(
    parser_fixture, result_queue_fixture, csmoney_responses_fixture
):
    await parser_fixture.parse(
        "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true",
        result_queue_fixture,
    )

    assert len(csmoney_responses_fixture.requests) == 4
    urls = {str(url): len(calls) for (_, url), calls in csmoney_responses_fixture.requests.items()}

    # asserting number of calls for each URL
    assert (
        urls[
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=0&withStack=true"
        ]
        == 1
    )
    assert (
        urls[
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=60&withStack=true"
        ]
        == 1
    )
    assert (
        urls[
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=120&withStack=true"
        ]
        == 1
    )
    assert (
        urls[
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=180&withStack=true"
        ]
        == 1
    )


async def test_parse_with_errors__assert_requests(
    parser_fixture, result_queue_fixture, csmoney_responses_with_errors_fixture
):
    await parser_fixture.parse(
        "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true",
        result_queue_fixture,
    )

    assert len(csmoney_responses_with_errors_fixture.requests) == 4
    urls = {
        str(url): len(calls)
        for (_, url), calls in csmoney_responses_with_errors_fixture.requests.items()
    }

    # asserting number of calls for each URL
    assert (
        urls[
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=0&withStack=true"
        ]
        == 1
    )
    assert (
        urls[
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=60&withStack=true"
        ]
        == 2
    )
    assert (
        urls[
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=120&withStack=true"
        ]
        == 3
    )
    assert (
        urls[
            "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=180&withStack=true"
        ]
        == 1
    )


@pytest.mark.parametrize("max_attempts", range(25))
async def test_parse_with_errors__check_max_attempts(
    parser_fixture, result_queue_fixture, max_attempts
):
    with aioresponses() as m:
        for _ in range(max_attempts + 10):
            m.get(
                "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true&offset=60",
                exception=aiohttp.ClientConnectionError(),
            )

        with pytest.raises(MaxAttemptsReachedError):
            await parser_fixture.parse(
                "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&withStack=true",
                result_queue_fixture,
                max_attempts=max_attempts,
            )

        assert len(m.requests) == 1
        urls = {str(url): len(calls) for (_, url), calls in m.requests.items()}
        # asserting number of calls for each URL
        assert (
            urls[
                "https://inventories.cs.money/5.0/load_bots_inventory/730?limit=60&offset=0&withStack=true"
            ]
            == max_attempts + 1
        )


if __name__ == "__main__":
    pytest.main()

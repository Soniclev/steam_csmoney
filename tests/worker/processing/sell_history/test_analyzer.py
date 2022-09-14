import json
from datetime import datetime

import pytest

from price_monitoring.worker.processing.sell_history.analyzer import SellHistoryAnalyzer


def _load_data(name: str) -> str:
    with open(f"tests/worker/processing/sell_history/{name}.json", "r", encoding="utf8") as f:
        return f.read()


@pytest.mark.parametrize("name", ["test_data", "test_data_2", "test_data_9"])
def test_analyze_history(name):
    analyzer = SellHistoryAnalyzer(_load_data(name))
    expected = {
        float(k): int(v) for k, v in json.loads(_load_data(name + "_expected"))["pairs"].items()
    }
    assert analyzer.analyze_history(current_dt=datetime(2022, 4, 22, 18)) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("test_data", 391982),
        ("test_data_2", 205),
    ],
)
def test_get_sold_amount_for_week(name, expected):
    analyzer = SellHistoryAnalyzer(_load_data(name))
    assert analyzer.get_sold_amount_for_week(current_dt=datetime(2022, 4, 22, 18)) == expected


def test_dump():
    encoded = '[["Sep 22 2021 01: +0",0.633,"286"],["Sep 23 2021 01: +0",0.675,"242"]]'
    analyzer = SellHistoryAnalyzer(encoded)
    assert analyzer.dump() == encoded


@pytest.mark.parametrize(
    "data, is_stable",
    [
        ("test_data", True),
        ("test_data_2", False),
        ("test_data_3", True),
        ("test_data_4", True),
        ("test_data_5", False),
        ("test_data_6", False),
        ("test_data_7", True),
        ("test_data_8", False),
        ("test_data_9", True),
        ("test_data_10", False),
    ],
)
def test_is_stable(data, is_stable):
    analyzer = SellHistoryAnalyzer(_load_data(data))
    assert analyzer.is_stable(current_dt=datetime(2022, 4, 23, 18)) == is_stable

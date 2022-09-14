from price_monitoring.features.overpay.overpay_reference import OverpayReference
from price_monitoring.features.overpay.overpay_sort import (
    sort_each_name_by_profit,
    sort_name_by_lowest_profit,
)

SOURCE = {
    "AK": [
        OverpayReference(market_name="AK", float_="0.002", overpay=0.4, base_price=2, sell_price=1),
        OverpayReference(market_name="AK", float_="0.001", overpay=0.5, base_price=2, sell_price=1),
    ],
    "M4A1": [
        OverpayReference(
            market_name="M4A1",
            float_="0.0023",
            overpay=0.4,
            base_price=2,
            sell_price=0.5,
        ),
        OverpayReference(
            market_name="M4A1",
            float_="0.0012",
            overpay=0.5,
            base_price=2,
            sell_price=0.5,
        ),
    ],
}

EXPECTED = {
    "M4A1": [
        OverpayReference(
            market_name="M4A1",
            float_="0.0012",
            overpay=0.5,
            base_price=2,
            sell_price=0.5,
        ),
        OverpayReference(
            market_name="M4A1",
            float_="0.0023",
            overpay=0.4,
            base_price=2,
            sell_price=0.5,
        ),
    ],
    "AK": [
        OverpayReference(market_name="AK", float_="0.001", overpay=0.5, base_price=2, sell_price=1),
        OverpayReference(market_name="AK", float_="0.002", overpay=0.4, base_price=2, sell_price=1),
    ],
}

EXPECTED_LOWEST = {
    "M4A1": OverpayReference(
        market_name="M4A1", float_="0.0023", overpay=0.4, base_price=2, sell_price=0.5
    ),
    "AK": OverpayReference(
        market_name="AK", float_="0.002", overpay=0.4, base_price=2, sell_price=1
    ),
}


def test_sort():
    assert sort_each_name_by_profit(SOURCE) == EXPECTED


def test_sort_lowest():
    assert sort_name_by_lowest_profit(SOURCE) == EXPECTED_LOWEST

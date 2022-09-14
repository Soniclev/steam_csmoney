import pytest

from price_monitoring.features.overpay.generate_list import adjust_float, generate_list
from price_monitoring.features.overpay.overpay_reference import OverpayReference


@pytest.mark.parametrize(
    "float_, expected",
    [
        ("0.01", "0.0101"),
        ("0.007", "0.00707"),
        ("0.004772999789565", "0.00482"),
        ("0.07697753608226701", "0.07774"),
        ("0.07697053608336746", "0.07774"),
    ],
)
def test_adjust_float(float_: str, expected):
    assert adjust_float(float_) == expected


def test_generate_list():
    overpay = OverpayReference(
        market_name="M4A1-S | Nightmare (Field-Tested)",
        float_="0.004772999789565",
        overpay=0.5,
        base_price=5,
        sell_price=4.12,
    )
    assert generate_list([overpay]) == [
        "https://steamcommunity.com/market/listings/730/"
        "M4A1-S%20%7C%20Nightmare%20%28Field-Tested%29 0.00482 $4.12"
    ]


def test_generate_list_skip_high_floats():
    overpay = OverpayReference(
        market_name="M4A1-S | Nightmare (Field-Tested)",
        float_="0.324772999789565",
        overpay=0.5,
        base_price=5,
        sell_price=4.12,
    )
    assert generate_list([overpay]) == []

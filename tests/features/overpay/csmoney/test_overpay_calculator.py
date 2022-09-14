import pytest

from price_monitoring.features.overpay.csmoney.overpay_calculator import compute_accept_price

TEST_DATA = [
    (0.23, 0.36, 0.54),
    (3.08, 1.24, 4.01),
    (12.67, 8.74, 19.90),
]

# 5% fee instead of 7%
TEST_DATA_WITH_5_FEE = [
    (9.56, 3.31, 12.22),
    (6.66, 2.34, 8.54),
    (5.75, 2.87, 8.18),
]


@pytest.mark.parametrize("pair", TEST_DATA)
def test_compute_accept_price(pair):
    base_price = pair[0]
    overpay = pair[1]
    expected = pair[2]
    assert compute_accept_price(base_price, overpay) == expected


@pytest.mark.parametrize("pair", TEST_DATA_WITH_5_FEE)
def test_compute_accept_price_with_5_fee(pair):
    base_price = pair[0]
    overpay = pair[1]
    expected = pair[2]
    assert compute_accept_price(base_price, overpay, commission=0.05) == expected

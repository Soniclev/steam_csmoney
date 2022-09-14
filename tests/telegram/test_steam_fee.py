import pytest

from price_monitoring.telegram.steam_fee import SteamFee


@pytest.mark.parametrize(
    "orig, expected",
    [
        (0.01, 0.00),
        (0.02, 0.00),
        (0.03, 0.01),
        (0.04, 0.02),
        (0.23, 0.2),
        (0.22, 0.19),
        (0.21, 0.19),
        (0.20, 0.18),
        (0.19, 0.17),
        (1.49, 1.3),
        (2.3, 2),
        (3.45, 3),
        (4.6, 4),
        (5.75, 5),
        (14.29, 12.43),
        (148.84, 129.43),
    ],
)
def test_subtract_fee(orig, expected):
    assert SteamFee.subtract_fee(orig) == expected


def test_subtract_fee_high():
    # test all prices from $0.01 to $10
    prev_price = None
    for i in range(1, 1001):
        price = round(i / 100, 2)
        price_with_fee = SteamFee.add_fee(price)
        assert SteamFee.subtract_fee(price_with_fee) == price
        # need to check corner cases, like:
        # 0.19 -> 0.21
        # 0.19 -> 0.22
        if prev_price:
            while price - 0.01 > prev_price:
                prev_price = round(prev_price + 0.01, 2)
                price_with_fee = SteamFee.add_fee(prev_price)
                assert SteamFee.subtract_fee(price_with_fee) == price
        prev_price = price


@pytest.mark.parametrize(
    "orig, expected",
    [
        (0.01, 0.03),
        (0.09, 0.11),
        (0.18, 0.2),
        (0.19, 0.21),
        (0.2, 0.23),
        (0.59, 0.66),
        (0.6, 0.69),
        (1.3, 1.49),
        (2, 2.3),
        (3, 3.45),
        (4, 4.60),
        (5, 5.75),
        (12.43, 14.29),
        (129.43, 148.84),
    ],
)
def test_add_fee(orig, expected):
    assert SteamFee.add_fee(orig) == expected

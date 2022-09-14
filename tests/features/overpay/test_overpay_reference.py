from price_monitoring.features.overpay.csmoney.overpay_calculator import compute_accept_price
from price_monitoring.features.overpay.overpay_reference import OverpayReference

overpay_reference = OverpayReference(
    market_name="AK", float_="0.00005706", overpay=0.5, base_price=1, sell_price=1.2
)

accept_price = compute_accept_price(base_price=1, overpay=0.5)


def test_compute_accept_price():
    assert overpay_reference.compute_accept_price() == accept_price


def test_compute_profit():
    assert overpay_reference.compute_profit() == accept_price - overpay_reference.sell_price


def test_compute_perc_profit():
    assert overpay_reference.compute_perc_profit() == 15.83  # 15.83%


def test_str():
    assert (
        str(overpay_reference) == "AK"
        "                                   "
        "                                  "
        "0.00005706                 1.39       1.20      15.83%"
    )

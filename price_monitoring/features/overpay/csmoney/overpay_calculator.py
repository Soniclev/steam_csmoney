import decimal
from decimal import Decimal


def _floor2(number: Decimal) -> Decimal:
    return number.quantize(Decimal("1.00"), decimal.ROUND_FLOOR)


def compute_accept_price(base_price: float, overpay: float, commission: float = 0.07) -> float:
    base_price = Decimal(str(base_price))
    overpay = Decimal(str(overpay))
    commission = Decimal(str(commission))

    multiplier = Decimal(1) - commission

    new_base_price = _floor2(base_price * multiplier)
    new_overpay = _floor2(overpay * multiplier)
    accept_price = _floor2(new_base_price + new_overpay)
    return float(accept_price)

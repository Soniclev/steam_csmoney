import decimal
import urllib.parse

from .overpay_reference import OverpayReference

_FLOAT_ADJUST = decimal.Decimal("1.01")
_FLOAT_ROUND = decimal.Decimal("1." + "0" * 5)


def adjust_float(float_: str) -> str:
    number = decimal.Decimal(float_) * _FLOAT_ADJUST
    number = number.quantize(_FLOAT_ROUND, decimal.ROUND_FLOOR)
    return str(number.normalize())


def generate_list(overpays: list[OverpayReference]) -> list[str]:
    def _generate(overpay: OverpayReference) -> str:
        quoted_name = urllib.parse.quote(overpay.market_name)
        adjusted_float = adjust_float(overpay.float_)
        return (
            f"https://steamcommunity.com/market/listings/730/"
            f"{quoted_name} {adjusted_float} ${overpay.sell_price}"
        )

    return [_generate(x) for x in overpays if x.float_ < "0.3"]

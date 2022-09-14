import math
from functools import lru_cache


class SteamFee:
    @staticmethod
    @lru_cache(maxsize=10**5)
    def subtract_fee(price: float) -> float:
        if price <= 0.02:
            return 0
        est_poor = round(price * 0.8, 2)

        while True:
            with_fee = SteamFee.add_fee(est_poor)
            if with_fee > price:
                break
            step = math.floor((price - with_fee) * 70) / 100
            est_poor += max(step, 0.01)
            est_poor = round(est_poor, 2)

        return round(est_poor - 0.01, 2)

    @staticmethod
    @lru_cache(maxsize=10**5)
    def add_fee(price: float) -> float:
        def _compute_fee(price_, perc_amount):
            fee = math.floor(price_ * perc_amount) / 100
            return max(round(fee, 2), 0.01)

        game = _compute_fee(price, 10)
        steam = _compute_fee(price, 5)
        return round(price + game + steam, 2)

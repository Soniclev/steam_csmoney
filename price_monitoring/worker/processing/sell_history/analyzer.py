import functools
import itertools
import json
import math
import operator
import statistics
from collections import defaultdict
from datetime import datetime, timedelta


_WINDOW_SLICING_SIZE = 15
_MAX_ALLOWED_STABLE_PRICE_DEVIATION = 0.06


def steam_date_str_to_datetime(s: str) -> datetime:
    """
    converts str like 'Mar 16 2017 01: +0' to datetime:
    """
    s = s[: s.index(":")]
    return datetime.strptime(s, "%b %d %Y %H")


def steam_round_price(price: float) -> float:
    """rounds price with precision 2"""
    return round(price, 2)


def percentage_diff(price1: float, price2: float) -> float:
    min_ = min(price1, price2)
    max_ = max(price1, price2)
    return (max_ - min_) / max_


def window_slicing(k, iter_):
    for i in range(0, len(iter_) - k + 1):
        yield iter_[i : i + k]


class SellHistoryAnalyzer:
    def __init__(self, encoded: str):
        j = json.loads(encoded)
        self.encoded = encoded
        self.start_day = None
        self._history = []
        for point in j:
            date, avg_price, amount = point
            date = steam_date_str_to_datetime(date)
            avg_price = steam_round_price(avg_price)
            amount = int(amount)
            assert amount != 0
            if self.start_day is None:
                self.start_day = date
            else:
                self.end_day = date
            self._history.append((date, avg_price, amount))

    def dump(self) -> str:
        return self.encoded

    def get_sold_amount_for_week(self, current_dt: datetime, duration=timedelta(days=7)) -> int:
        history = self.peek_points(current_dt=current_dt, duration=duration)
        sells = map(lambda x: x[2], history)  # sell amount
        return sum(sells)

    def is_stable(self, current_dt: datetime) -> bool:
        history = self.peek_points(current_dt=current_dt)
        slices = window_slicing(_WINDOW_SLICING_SIZE, history)
        slices = tuple(slices)
        slices_mean_prices = tuple(
            statistics.harmonic_mean(
                data=map(operator.itemgetter(1), slice_),  # price
                weights=map(operator.itemgetter(2), slice_),  # sold amount
            )
            for slice_ in slices
        )
        slices_mean_prices = map(functools.partial(round, ndigits=2), slices_mean_prices)
        slices_mean_prices = tuple(slices_mean_prices)
        if len(slices_mean_prices) < 5:
            return False
        mean_min = min(slices_mean_prices)
        mean_max = max(slices_mean_prices)
        med = statistics.median(slices_mean_prices)
        perc_diff_min = percentage_diff(mean_min, med)
        perc_diff_max = percentage_diff(mean_max, med)
        deviation = statistics.stdev(slices_mean_prices) / med
        fall_deviation = statistics.stdev([slices_mean_prices[0], slices_mean_prices[-1]]) / med
        is_fall = slices_mean_prices[0] < slices_mean_prices[-1] and fall_deviation > 0.01
        is_low_deviation = deviation < _MAX_ALLOWED_STABLE_PRICE_DEVIATION
        is_min_ok = perc_diff_min < 0.1
        is_max_ok = perc_diff_max < 0.1
        is_ok = is_min_ok and is_max_ok
        return not is_fall and is_low_deviation and is_ok

    def peek_points(
        self,
        current_dt: datetime,
        duration: timedelta = timedelta(days=7),
    ) -> tuple[tuple[datetime, float, int], ...]:
        stop_datetime = current_dt - duration
        return tuple(itertools.takewhile(lambda x: x[0] > stop_datetime, reversed(self._history)))

    def analyze_history(
        self, current_dt: datetime, duration=timedelta(days=7)
    ) -> dict[float, float]:
        history = self.peek_points(duration=duration, current_dt=current_dt)
        sold_dict: dict[float, int] = defaultdict(int)
        for _, price, amount in history:
            sold_dict[price] += amount

        sold_dict = dict(sorted(sold_dict.items(), key=operator.itemgetter(0)))

        total_sold = sum(sold_dict.values())
        current_percentage = 0.0
        result: dict[float, float] = {}
        for price, amount in sold_dict.items():
            step = amount / total_sold * 100
            result[price] = 100 - math.floor(current_percentage)
            current_percentage += step
        return result

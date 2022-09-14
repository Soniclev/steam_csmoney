from typing import TypeAlias

from .overpay_reference import OverpayReference
from ...types import MarketName

OverpayTuple: TypeAlias = tuple[MarketName, list[OverpayReference]]
SkinOverpays: TypeAlias = dict[MarketName, list[OverpayReference]]
SkinOverpay: TypeAlias = dict[MarketName, OverpayReference]


def _sort_key(overpay: OverpayReference):
    return overpay.compute_perc_profit()


def _sort_key_for_list_max(tuple_: OverpayTuple) -> float:
    return max(map(_sort_key, tuple_[1]))


def _sort_key_for_list_min(tuple_: OverpayTuple) -> float:
    return min(map(_sort_key, tuple_[1]))


def sort_each_name_by_profit(dict_: SkinOverpays) -> SkinOverpays:
    # noinspection PyTypeChecker
    sorted_names = sorted(dict_.items(), key=_sort_key_for_list_max, reverse=True)
    sorted_each_name = {k: sorted(v, key=_sort_key, reverse=True) for k, v in sorted_names}
    return sorted_each_name


def sort_name_by_lowest_profit(dict_: SkinOverpays) -> SkinOverpay:
    # noinspection PyTypeChecker
    sorted_names = sorted(dict_.items(), key=_sort_key_for_list_min, reverse=True)
    sorted_each_name = {k: sorted(v, key=_sort_key, reverse=True)[-1] for k, v in sorted_names}
    return sorted_each_name

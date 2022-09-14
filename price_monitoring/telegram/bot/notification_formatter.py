import typing

from aiogram.utils import markdown

from ..models import ItemOfferNotification
from ..steam_fee import SteamFee


def to_markdown(notification: ItemOfferNotification) -> str:
    price_with_fee = SteamFee.add_fee(notification.sell_price)
    # 1.0%  $1.14 -> $0.98 ($0.98)  AUTOBUY
    # pylint: disable=consider-using-f-string
    block = "{}  {} \\-\\> {} {}  {}".format(
        markdown.bold(f"{notification.compute_percentage_diff()}%"),
        markdown.escape_md(f"${notification.orig_price}"),
        markdown.escape_md(f"${notification.sell_price}"),
        markdown.escape_md(f"(${price_with_fee})"),
        markdown.italic(notification.short_title),
    )

    full_name = markdown.code(notification.market_name)

    link = markdown.link(
        notification.market_name,
        markdown.escape_md(
            "https://steamcommunity.com/market/listings/730/" + notification.market_name
        ),
    )

    return "\n".join([block, full_name, link])


def several_to_markdown(notifications: typing.Iterable[ItemOfferNotification]) -> str:
    return "\n\n".join(to_markdown(notification) for notification in notifications)

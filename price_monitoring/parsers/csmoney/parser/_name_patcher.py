import re

from ....types import MarketName

_PATTERN = r" Doppler ((Phase \d+)|Sapphire|Ruby|Black Pearl|Emerald)"


def patch_market_name(market_name: str) -> MarketName:
    return re.sub(_PATTERN, " Doppler", market_name)

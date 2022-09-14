import pytest

from price_monitoring.models.steam import SkinSellHistory


@pytest.mark.parametrize(
    "max_level, expected",
    [
        (50, 1.06),
        (51, 1.05),
        (49, 1.06),
        (40, 1.07),
        (10, 1.07),
        (61, None),
    ],
)
def test_get(max_level, expected):
    summary = SkinSellHistory(
        market_name="AK", is_stable=True, sold_per_week=150, summary={1.05: 60, 1.06: 50, 1.07: 40}
    )

    assert summary.get(max_level) == expected

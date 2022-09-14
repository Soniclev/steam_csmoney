import pytest

from price_monitoring.parsers.csmoney.parser._name_patcher import patch_market_name


@pytest.mark.parametrize(
    "src,expected",
    [
        ("★ Sport Gloves | Vice (Factory New)", "★ Sport Gloves | Vice (Factory New)"),
        (
            "Souvenir Glock-18 | Nuclear Garden (Factory New)",
            "Souvenir Glock-18 | Nuclear Garden (Factory New)",
        ),
        (
            "★ Butterfly Knife | Doppler Sapphire (Factory New)",
            "★ Butterfly Knife | Doppler (Factory New)",
        ),
        (
            "★ M9 Bayonet | Gamma Doppler Emerald (Minimal Wear)",
            "★ M9 Bayonet | Gamma Doppler (Minimal Wear)",
        ),
        (
            "★ Butterfly Knife | Doppler Ruby (Factory New)",
            "★ Butterfly Knife | Doppler (Factory New)",
        ),
        (
            "★ Talon Knife | Doppler Black Pearl (Minimal Wear)",
            "★ Talon Knife | Doppler (Minimal Wear)",
        ),
        (
            "★ Butterfly Knife | Gamma Doppler Phase 1 (Minimal Wear)",
            "★ Butterfly Knife | Gamma Doppler (Minimal Wear)",
        ),
        (
            "★ Butterfly Knife | Gamma Doppler Phase 2 (Minimal Wear)",
            "★ Butterfly Knife | Gamma Doppler (Minimal Wear)",
        ),
        (
            "★ Butterfly Knife | Gamma Doppler Phase 3 (Minimal Wear)",
            "★ Butterfly Knife | Gamma Doppler (Minimal Wear)",
        ),
        (
            "★ Butterfly Knife | Gamma Doppler Phase 4 (Minimal Wear)",
            "★ Butterfly Knife | Gamma Doppler (Minimal Wear)",
        ),
    ],
)
def test_patch_market_name(src, expected):
    assert patch_market_name(src) == expected

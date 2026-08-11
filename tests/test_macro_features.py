import pandas as pd

from atlas.macro.features import (
    build_macro_features,
    classify_regimes,
)


def test_yield_curve_is_10y_minus_2y():
    dates = pd.date_range("2024-01-31", periods=15, freq="ME")

    macro = pd.DataFrame(
        {
            "CPIAUCSL": range(100, 115),
            "INDPRO": range(100, 115),
            "FEDFUNDS": [5.0] * 15,
            "DGS2": [4.0] * 15,
            "DGS10": [4.5] * 15,
        },
        index=dates,
    )

    features = build_macro_features(macro)

    assert features["yield_curve_10y_2y"].iloc[-1] == 0.5


def test_expansion_regime():
    features = pd.DataFrame(
        {
            "growth_trend_3m": [1.0],
            "inflation_trend_3m": [-0.5],
        },
        index=[pd.Timestamp("2026-01-31")],
    )

    regimes = classify_regimes(features)

    assert regimes.iloc[0] == "expansion"


def test_stagflation_regime():
    features = pd.DataFrame(
        {
            "growth_trend_3m": [-1.0],
            "inflation_trend_3m": [0.5],
        },
        index=[pd.Timestamp("2026-01-31")],
    )

    regimes = classify_regimes(features)

    assert regimes.iloc[0] == "stagflation"
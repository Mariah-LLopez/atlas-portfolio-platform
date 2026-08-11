import numpy as np
import pandas as pd

from atlas.signals.momentum import cross_sectional_zscore, momentum_12_1


def test_momentum_12_1_uses_prior_month_and_twelve_month_lag():
    dates = pd.date_range("2024-01-31", periods=14, freq="ME")
    prices = pd.DataFrame({"A": np.arange(100, 114, dtype=float)}, index=dates)

    signal = momentum_12_1(prices)

    expected = prices.iloc[12]["A"] / prices.iloc[1]["A"] - 1.0
    assert np.isclose(signal.iloc[13]["A"], expected)


def test_cross_sectional_zscore_has_zero_cross_sectional_mean():
    signal = pd.DataFrame(
        [[1.0, 2.0, 3.0]],
        index=[pd.Timestamp("2026-01-31")],
        columns=["A", "B", "C"],
    )
    z = cross_sectional_zscore(signal)
    assert np.isclose(z.iloc[0].mean(), 0.0)

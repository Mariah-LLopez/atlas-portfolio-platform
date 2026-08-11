import numpy as np
import pandas as pd

from atlas.signals.risk import rolling_annualized_volatility


def test_constant_returns_have_zero_volatility():
    returns = pd.DataFrame(
        {"A": [0.01] * 10},
        index=pd.bdate_range("2026-01-01", periods=10),
    )
    vol = rolling_annualized_volatility(returns, window=5)
    assert np.isclose(vol.dropna().iloc[-1]["A"], 0.0)

import numpy as np
import pandas as pd

from atlas.backtest.metrics import (
    annualized_volatility,
    cumulative_wealth,
    max_drawdown,
)


def test_zero_returns_have_zero_volatility():
    returns = pd.Series(
        [0.0] * 252
    )

    assert np.isclose(
        annualized_volatility(returns),
        0.0,
    )


def test_cumulative_wealth_compounds_returns():
    returns = pd.Series(
        [0.10, 0.10]
    )

    wealth = cumulative_wealth(returns)

    assert np.isclose(
        wealth.iloc[-1],
        1.21,
    )


def test_max_drawdown_detects_decline():
    returns = pd.Series(
        [0.10, -0.20, 0.05]
    )

    assert max_drawdown(returns) < 0
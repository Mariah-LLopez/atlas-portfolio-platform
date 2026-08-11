import numpy as np
import pandas as pd
import pytest

from atlas.backtest.benchmarks import (
    constant_weight_portfolio_returns,
    equal_weight_benchmark,
    sixty_forty_benchmark,
)


def test_constant_weight_portfolio_return():
    returns = pd.DataFrame(
        {
            "A": [0.10],
            "B": [0.00],
        }
    )

    weights = pd.Series(
        {
            "A": 0.50,
            "B": 0.50,
        }
    )

    result = constant_weight_portfolio_returns(
        returns,
        weights,
    )

    assert np.isclose(
        result.iloc[0],
        0.05,
    )


def test_equal_weight_benchmark():
    returns = pd.DataFrame(
        {
            "A": [0.10],
            "B": [0.00],
        }
    )

    result = equal_weight_benchmark(
        returns
    )

    assert np.isclose(
        result.iloc[0],
        0.05,
    )


def test_sixty_forty_benchmark():
    returns = pd.DataFrame(
        {
            "SPY": [0.10],
            "IEF": [0.00],
        }
    )

    result = sixty_forty_benchmark(
        returns
    )

    assert np.isclose(
        result.iloc[0],
        0.06,
    )


def test_invalid_weights_fail():
    returns = pd.DataFrame(
        {
            "A": [0.10],
            "B": [0.00],
        }
    )

    weights = pd.Series(
        {
            "A": 0.80,
            "B": 0.80,
        }
    )

    with pytest.raises(ValueError):
        constant_weight_portfolio_returns(
            returns,
            weights,
        )
import numpy as np
import pandas as pd

from atlas.cma.assumptions import annualized_covariance, demonstration_expected_returns


def test_positive_momentum_increases_expected_return():
    dates = pd.bdate_range("2024-01-01", periods=300)
    returns = pd.DataFrame(
        {"A": [0.0002] * len(dates), "B": [0.0002] * len(dates)},
        index=dates,
    )
    momentum_z = pd.Series({"A": 1.0, "B": -1.0})
    er = demonstration_expected_returns(
        returns,
        momentum_z,
        years=1,
        momentum_tilt=0.02,
    )
    assert er["A"] > er["B"]


def test_covariance_is_square_and_labeled():
    dates = pd.bdate_range("2024-01-01", periods=300)
    rng = np.random.default_rng(1)
    returns = pd.DataFrame(
        rng.normal(0, 0.01, size=(len(dates), 2)),
        index=dates,
        columns=["A", "B"],
    )
    cov = annualized_covariance(returns, years=1)
    assert cov.shape == (2, 2)
    assert list(cov.index) == ["A", "B"]
    assert list(cov.columns) == ["A", "B"]

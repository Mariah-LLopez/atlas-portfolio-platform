import numpy as np
import pandas as pd
import pytest

from atlas.portfolio.optimizer import optimize_portfolio


@pytest.fixture
def optimizer_inputs():
    assets = ["SPY", "VXUS", "IEF", "GLD", "BIL"]

    expected_returns = pd.Series(
        {
            "SPY": 0.08,
            "VXUS": 0.07,
            "IEF": 0.04,
            "GLD": 0.05,
            "BIL": 0.03,
        }
    )

    covariance = pd.DataFrame(
        np.diag(
            [
                0.04,
                0.04,
                0.01,
                0.02,
                0.001,
            ]
        ),
        index=assets,
        columns=assets,
    )

    max_weights = pd.Series(
        {
            "SPY": 0.40,
            "VXUS": 0.30,
            "IEF": 0.40,
            "GLD": 0.20,
            "BIL": 0.30,
        }
    )

    return expected_returns, covariance, max_weights


def test_optimizer_weights_sum_to_one(
    optimizer_inputs,
):
    expected_returns, covariance, max_weights = optimizer_inputs

    weights = optimize_portfolio(
        expected_returns,
        covariance,
        max_weights,
    )

    assert np.isclose(
        weights.sum(),
        1.0,
        atol=1e-6,
    )


def test_optimizer_respects_asset_caps(
    optimizer_inputs,
):
    expected_returns, covariance, max_weights = optimizer_inputs

    weights = optimize_portfolio(
        expected_returns,
        covariance,
        max_weights,
    )

    assert (
        weights
        <= max_weights + 1e-6
    ).all()


def test_optimizer_respects_cash_floor(
    optimizer_inputs,
):
    expected_returns, covariance, max_weights = optimizer_inputs

    weights = optimize_portfolio(
        expected_returns,
        covariance,
        max_weights,
        min_cash_weight=0.05,
    )

    assert weights["BIL"] >= 0.05 - 1e-6


def test_optimizer_respects_equity_cap(
    optimizer_inputs,
):
    expected_returns, covariance, max_weights = optimizer_inputs

    weights = optimize_portfolio(
        expected_returns,
        covariance,
        max_weights,
        equity_assets=["SPY", "VXUS"],
        max_equity_weight=0.50,
    )

    equity_weight = (
        weights["SPY"]
        + weights["VXUS"]
    )

    assert equity_weight <= 0.50 + 1e-6


def test_optimizer_rejects_invalid_risk_aversion(
    optimizer_inputs,
):
    expected_returns, covariance, max_weights = optimizer_inputs

    with pytest.raises(ValueError):
        optimize_portfolio(
            expected_returns,
            covariance,
            max_weights,
            risk_aversion=0,
        )

def test_turnover_never_exceeds_policy_limit(
    optimizer_inputs,
):
    expected_returns, covariance, max_weights = (
        optimizer_inputs
    )

    previous_weights = pd.Series(
        {
            "SPY": 0.20,
            "VXUS": 0.20,
            "IEF": 0.20,
            "GLD": 0.20,
            "BIL": 0.20,
        }
    )

    policy_limit = 0.20

    weights = optimize_portfolio(
        expected_returns,
        covariance,
        max_weights,
        previous_weights=previous_weights,
        max_turnover=policy_limit,
        turnover_penalty=0.002,
    )

    realized_turnover = (
        weights
        .sub(previous_weights)
        .abs()
        .sum()
        / 2.0
    )

    assert (
        realized_turnover
        <= policy_limit
    )
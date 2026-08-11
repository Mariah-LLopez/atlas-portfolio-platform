import numpy as np
import pandas as pd

from atlas.backtest.engine import (
    run_walk_forward_backtest,
)


def build_test_inputs():
    rng = np.random.default_rng(42)

    dates = pd.bdate_range(
        "2023-01-02",
        periods=550,
    )

    assets = [
        "SPY",
        "GLD",
        "BIL",
    ]

    returns = pd.DataFrame(
        {
            "SPY": rng.normal(
                0.0003,
                0.01,
                len(dates),
            ),
            "GLD": rng.normal(
                0.0002,
                0.008,
                len(dates),
            ),
            "BIL": rng.normal(
                0.0001,
                0.0005,
                len(dates),
            ),
        },
        index=dates,
    )

    month_ends = (
        returns
        .resample("ME")
        .last()
        .index
    )

    momentum_z = pd.DataFrame(
        {
            "SPY": 0.5,
            "GLD": 0.0,
            "BIL": -0.5,
        },
        index=month_ends,
    )

    macro_regimes = pd.Series(
        "expansion",
        index=month_ends,
        name="macro_regime",
        dtype="string",
    )

    max_weights = pd.Series(
        {
            "SPY": 0.70,
            "GLD": 0.50,
            "BIL": 0.50,
        }
    )

    return (
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
    )


def test_backtest_produces_returns():
    (
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
    ) = build_test_inputs()

    result = run_walk_forward_backtest(
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
        history_years=1,
        minimum_history_days=120,
        cash_asset="BIL",
        min_cash_weight=0.05,
        equity_assets=["SPY"],
        max_equity_weight=0.70,
    )

    assert not result.portfolio_returns.empty


def test_backtest_weights_sum_to_one():
    (
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
    ) = build_test_inputs()

    result = run_walk_forward_backtest(
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
        history_years=1,
        minimum_history_days=120,
        cash_asset="BIL",
        min_cash_weight=0.05,
        equity_assets=["SPY"],
        max_equity_weight=0.70,
    )

    totals = result.weights.sum(
        axis=1
    )

    assert np.allclose(
        totals,
        1.0,
        atol=1e-6,
    )


def test_backtest_turnover_is_nonnegative():
    (
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
    ) = build_test_inputs()

    result = run_walk_forward_backtest(
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
        history_years=1,
        minimum_history_days=120,
        cash_asset="BIL",
        min_cash_weight=0.05,
        equity_assets=["SPY"],
        max_equity_weight=0.70,
    )

    assert (
        result.turnover >= 0
    ).all()


def test_backtest_respects_cash_floor():
    (
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
    ) = build_test_inputs()

    result = run_walk_forward_backtest(
        returns,
        momentum_z,
        macro_regimes,
        max_weights,
        history_years=1,
        minimum_history_days=120,
        cash_asset="BIL",
        min_cash_weight=0.05,
        equity_assets=["SPY"],
        max_equity_weight=0.70,
    )

    assert (
        result.weights["BIL"]
        >= 0.05 - 1e-6
    ).all()
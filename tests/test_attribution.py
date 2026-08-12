import numpy as np
import pandas as pd

from atlas.attribution.contribution import (
    build_attribution_summary,
    build_daily_attribution,
    build_monthly_attribution,
    reconciliation_error,
)


def build_inputs():
    dates = pd.bdate_range(
        "2026-01-01",
        "2026-02-27",
    )

    returns = pd.DataFrame(
        {
            "SPY": 0.001,
            "GLD": 0.002,
            "BIL": 0.0001,
        },
        index=dates,
    )

    weights = pd.DataFrame(
        {
            "SPY": [
                0.50,
                0.40,
            ],
            "GLD": [
                0.30,
                0.40,
            ],
            "BIL": [
                0.20,
                0.20,
            ],
        },
        index=pd.to_datetime(
            [
                "2025-12-31",
                "2026-01-31",
            ]
        ),
    )

    turnover = pd.Series(
        [
            0.0,
            0.10,
        ],
        index=weights.index,
        name="turnover",
    )

    return (
        returns,
        weights,
        turnover,
    )


def test_daily_contributions_sum_to_portfolio_return():
    returns, weights, turnover = (
        build_inputs()
    )

    attribution = build_daily_attribution(
        returns,
        weights,
        turnover=turnover,
        transaction_cost_bps=5.0,
    )

    contribution_columns = [
        "SPY",
        "GLD",
        "BIL",
        "transaction_cost",
    ]

    calculated = (
        attribution[
            contribution_columns
        ]
        .sum(axis=1)
    )

    assert np.allclose(
        calculated,
        attribution[
            "portfolio_return"
        ],
    )


def test_transaction_cost_is_negative():
    returns, weights, turnover = (
        build_inputs()
    )

    attribution = build_daily_attribution(
        returns,
        weights,
        turnover=turnover,
        transaction_cost_bps=5.0,
    )

    assert (
        attribution[
            "transaction_cost"
        ]
        <= 0
    ).all()


def test_monthly_attribution_has_portfolio_total():
    returns, weights, turnover = (
        build_inputs()
    )

    daily = build_daily_attribution(
        returns,
        weights,
        turnover=turnover,
        transaction_cost_bps=5.0,
    )

    monthly = build_monthly_attribution(
        daily
    )

    expected = (
        monthly[
            [
                "SPY",
                "GLD",
                "BIL",
                "transaction_cost",
            ]
        ]
        .sum(axis=1)
    )

    assert np.allclose(
        expected,
        monthly[
            "portfolio_return"
        ],
    )


def test_summary_contains_each_asset():
    returns, weights, turnover = (
        build_inputs()
    )

    daily = build_daily_attribution(
        returns,
        weights,
        turnover=turnover,
        transaction_cost_bps=5.0,
    )

    summary = (
        build_attribution_summary(
            daily
        )
    )

    assert "SPY" in summary.index
    assert "GLD" in summary.index
    assert "BIL" in summary.index
    assert (
        "transaction_cost"
        in summary.index
    )


def test_reconciliation_error_is_zero():
    returns, weights, turnover = (
        build_inputs()
    )

    daily = build_daily_attribution(
        returns,
        weights,
        turnover=turnover,
        transaction_cost_bps=5.0,
    )

    error = reconciliation_error(
        daily[
            "portfolio_return"
        ],
        daily[
            "portfolio_return"
        ],
    )

    assert np.isclose(
        error,
        0.0,
    )
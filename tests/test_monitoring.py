import pandas as pd

from atlas.monitoring.health import (
    check_cash_floor,
    check_equity_limit,
    check_portfolio_weights,
    check_turnover_limit,
    overall_status,
)


def test_valid_portfolio_is_healthy():
    weights = pd.Series(
        {
            "SPY": 0.40,
            "VXUS": 0.10,
            "GLD": 0.20,
            "BIL": 0.30,
        }
    )

    checks = [
        check_portfolio_weights(
            weights
        ),
        check_equity_limit(
            weights,
            equity_assets=[
                "SPY",
                "VXUS",
            ],
            maximum=0.60,
        ),
        check_cash_floor(
            weights,
            cash_asset="BIL",
            minimum=0.02,
        ),
    ]

    assert (
        overall_status(checks)
        == "HEALTHY"
    )


def test_turnover_breach_fails():
    turnover = pd.Series(
        [
            0.10,
            0.15,
            0.25,
        ]
    )

    check = check_turnover_limit(
        turnover,
        maximum=0.20,
    )

    assert check.status == "FAIL"
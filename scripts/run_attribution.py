from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from atlas.attribution.contribution import (
    build_attribution_summary,
    build_daily_attribution,
    build_monthly_attribution,
    reconciliation_error,
)
from atlas.config import load_yaml

DATA = Path("data/processed")


def main() -> None:
    print("Loading Atlas backtest outputs...")

    returns = pd.read_parquet(
        DATA / "market_returns.parquet"
    )

    weights = pd.read_parquet(
        DATA / "backtest_weights.parquet"
    )

    turnover_frame = pd.read_parquet(
        DATA / "backtest_turnover.parquet"
    )

    turnover = turnover_frame["turnover"]

    backtest_returns = pd.read_parquet(
        DATA / "backtest_returns.parquet"
    )

    portfolio_config = load_yaml(
        "configs/portfolio.yaml"
    )

    portfolio_settings = portfolio_config[
        "portfolio"
    ]

    transaction_cost_bps = float(
        portfolio_settings[
            "transaction_cost_bps"
        ]
    )

    print("Calculating daily attribution...")

    daily = build_daily_attribution(
        returns=returns,
        weights_history=weights,
        turnover=turnover,
        transaction_cost_bps=transaction_cost_bps,
    )

    print("Calculating monthly attribution...")

    monthly = build_monthly_attribution(
        daily
    )

    print("Building attribution summary...")

    summary = build_attribution_summary(
        daily
    )

    error = reconciliation_error(
        daily["portfolio_return"],
        backtest_returns["atlas"],
    )

    daily.to_parquet(
        DATA / "attribution_daily.parquet"
    )

    monthly.to_parquet(
        DATA / "attribution_monthly.parquet"
    )

    summary.to_parquet(
        DATA / "attribution_summary.parquet"
    )

    report = {
        "maximum_daily_reconciliation_error": error,
        "transaction_cost_bps": transaction_cost_bps,
        "observation_count": len(daily),
    }

    (
        DATA / "attribution_report.json"
    ).write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nAttribution complete.")

    print(
        "\nTotal arithmetic contribution by source:"
    )

    display = (
        summary["total_contribution"]
        .sort_values(
            ascending=False
        )
        .to_frame()
    )

    display["total_contribution"] = (
        display["total_contribution"]
        * 100
    )

    print(
        display
        .round(2)
        .to_string()
    )

    print(
        "\nMaximum daily reconciliation error:"
    )

    print(
        f"{error:.12f}"
    )

    print(
        "\nLatest 12 months of attribution:"
    )

    latest = (
        monthly
        .tail(12)
        .copy()
        * 100
    )

    print(
        latest
        .round(2)
        .to_string()
    )

    print("\nSaved:")
    print(
        "data/processed/attribution_daily.parquet"
    )
    print(
        "data/processed/attribution_monthly.parquet"
    )
    print(
        "data/processed/attribution_summary.parquet"
    )
    print(
        "data/processed/attribution_report.json"
    )


if __name__ == "__main__":
    main()
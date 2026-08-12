from __future__ import annotations

from pathlib import Path

import pandas as pd

from atlas.portfolio.rebalance import build_rebalance_orders


DATA = Path("data/processed")
SAMPLE = Path("data/sample")


def main() -> None:
    print("Loading current holdings...")

    holdings_frame = pd.read_csv(
        SAMPLE / "current_holdings.csv"
    )

    current_holdings = (
        holdings_frame
        .set_index("ticker")["market_value"]
        .astype(float)
    )

    print("Loading Atlas target portfolio...")

    target_frame = pd.read_parquet(
        DATA / "optimized_weights.parquet"
    )

    target_weights = (
        target_frame["weight"]
        .astype(float)
    )

    print("Loading latest market prices...")

    market_prices = pd.read_parquet(
        DATA / "market_prices.parquet"
    )

    latest_prices = (
        market_prices
        .dropna(how="all")
        .iloc[-1]
        .astype(float)
    )

    print("Generating rebalance orders...")

    orders = build_rebalance_orders(
        current_holdings=current_holdings,
        target_weights=target_weights,
        latest_prices=latest_prices,
        min_trade_dollars=500.0,
    )

    output = (
        DATA / "rebalance_orders.parquet"
    )

    orders.to_parquet(output)

    portfolio_value = float(
        current_holdings.sum()
    )

    estimated_turnover = (
        orders["trade_value"]
        .abs()
        .sum()
        / (2.0 * portfolio_value)
    )

    print("\nRebalance complete.")

    print(
        f"Portfolio value: "
        f"${portfolio_value:,.2f}"
    )

    print(
        f"Estimated turnover: "
        f"{estimated_turnover:.2%}"
    )

    display = orders[
        [
            "current_weight",
            "target_weight",
            "trade_value",
            "estimated_shares",
            "action",
        ]
    ].copy()

    display["current_weight"] = (
        display["current_weight"]
        * 100
    ).round(2)

    display["target_weight"] = (
        display["target_weight"]
        * 100
    ).round(2)

    display["trade_value"] = (
        display["trade_value"]
        .round(2)
    )

    display["estimated_shares"] = (
        display["estimated_shares"]
        .round(2)
    )

    print("\nProposed orders:")

    print(
        display.to_string()
    )

    print(
        f"\nSaved: {output}"
    )


if __name__ == "__main__":
    main()
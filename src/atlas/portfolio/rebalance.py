from __future__ import annotations

import numpy as np
import pandas as pd


class RebalanceError(RuntimeError):
    """Raised when a rebalance cannot be calculated safely."""


def build_rebalance_orders(
    current_holdings: pd.Series,
    target_weights: pd.Series,
    latest_prices: pd.Series,
    *,
    min_trade_dollars: float = 500.0,
) -> pd.DataFrame:
    """Create dollar and estimated-share rebalance orders.

    Parameters
    ----------
    current_holdings:
        Current market value by ticker.

    target_weights:
        Desired portfolio weight by ticker.

    latest_prices:
        Latest available market price by ticker.

    min_trade_dollars:
        Trades smaller than this amount are classified as HOLD.

    Returns
    -------
    pd.DataFrame
        Current allocation, target allocation, and proposed orders.
    """

    if current_holdings.empty:
        raise ValueError(
            "Current holdings cannot be empty."
        )

    if target_weights.empty:
        raise ValueError(
            "Target weights cannot be empty."
        )

    if min_trade_dollars < 0:
        raise ValueError(
            "min_trade_dollars cannot be negative."
        )

    assets = target_weights.index.tolist()

    holdings = current_holdings.reindex(
        assets
    ).fillna(0.0)

    prices = latest_prices.reindex(
        assets
    )

    if prices.isna().any():
        missing = (
            prices[
                prices.isna()
            ]
            .index
            .tolist()
        )

        raise RebalanceError(
            f"Missing prices for assets: {missing}"
        )

    if (
        prices <= 0
    ).any():
        bad = (
            prices[
                prices <= 0
            ]
            .index
            .tolist()
        )

        raise RebalanceError(
            f"Non-positive prices for assets: {bad}"
        )

    if (
        holdings < 0
    ).any():
        raise RebalanceError(
            "Current holdings cannot contain "
            "negative market values."
        )

    portfolio_value = float(
        holdings.sum()
    )

    if portfolio_value <= 0:
        raise RebalanceError(
            "Portfolio value must be positive."
        )

    if not np.isclose(
        target_weights.sum(),
        1.0,
        atol=1e-6,
    ):
        raise RebalanceError(
            "Target weights must sum to 1."
        )

    if (
        target_weights < -1e-8
    ).any():
        raise RebalanceError(
            "Target weights cannot be negative."
        )

    current_weights = (
        holdings
        / portfolio_value
    )

    target_values = (
        target_weights
        * portfolio_value
    )

    trade_values = (
        target_values
        - holdings
    )

    estimated_shares = (
        trade_values
        / prices
    )

    action = pd.Series(
        "HOLD",
        index=assets,
        dtype="string",
    )

    action.loc[
        trade_values
        >= min_trade_dollars
    ] = "BUY"

    action.loc[
        trade_values
        <= -min_trade_dollars
    ] = "SELL"

    executable_trade = trade_values.copy()

    executable_trade.loc[
        trade_values.abs()
        < min_trade_dollars
    ] = 0.0

    result = pd.DataFrame(
        {
            "current_value": holdings,
            "current_weight": current_weights,
            "target_weight": target_weights,
            "target_value": target_values,
            "trade_value": trade_values,
            "executable_trade_value": executable_trade,
            "latest_price": prices,
            "estimated_shares": estimated_shares,
            "action": action,
        }
    )

    result.index.name = "ticker"

    return result
from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_return(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """Calculate geometric annualized return."""
    clean = returns.dropna()

    if clean.empty:
        return float("nan")

    growth = (1.0 + clean).prod()
    years = len(clean) / periods_per_year

    if years <= 0:
        return float("nan")

    return float(
        growth ** (1.0 / years) - 1.0
    )


def annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """Calculate annualized realized volatility."""
    clean = returns.dropna()

    if clean.empty:
        return float("nan")

    return float(
        clean.std()
        * np.sqrt(periods_per_year)
    )


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Calculate annualized Sharpe ratio."""
    ann_return = annualized_return(
        returns,
        periods_per_year,
    )

    ann_vol = annualized_volatility(
        returns,
        periods_per_year,
    )

    if ann_vol == 0 or np.isnan(ann_vol):
        return float("nan")

    return float(
        (ann_return - risk_free_rate)
        / ann_vol
    )


def max_drawdown(
    returns: pd.Series,
) -> float:
    """Calculate maximum peak-to-trough drawdown."""
    wealth = (
        1.0 + returns.fillna(0.0)
    ).cumprod()

    running_peak = wealth.cummax()

    drawdown = (
        wealth / running_peak
        - 1.0
    )

    return float(drawdown.min())


def cumulative_wealth(
    returns: pd.Series,
    starting_value: float = 1.0,
) -> pd.Series:
    """Convert periodic returns into a wealth index."""
    return (
        starting_value
        * (1.0 + returns.fillna(0.0)).cumprod()
    )
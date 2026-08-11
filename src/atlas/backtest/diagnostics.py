from __future__ import annotations

import pandas as pd


def average_weights(
    weights: pd.DataFrame,
) -> pd.Series:
    """Average portfolio allocation through the backtest."""
    return weights.mean().rename("average_weight")


def maximum_weights(
    weights: pd.DataFrame,
) -> pd.Series:
    """Maximum observed allocation to each asset."""
    return weights.max().rename("maximum_weight")


def minimum_weights(
    weights: pd.DataFrame,
) -> pd.Series:
    """Minimum observed allocation to each asset."""
    return weights.min().rename("minimum_weight")


def concentration_rate(
    weights: pd.DataFrame,
    threshold: float = 0.399,
) -> pd.Series:
    """Share of rebalances where an asset is near a 40% cap."""
    return (
        weights.ge(threshold)
        .mean()
        .rename("concentration_rate")
    )


def zero_weight_rate(
    weights: pd.DataFrame,
    tolerance: float = 1e-6,
) -> pd.Series:
    """Share of rebalances where an asset is effectively unused."""
    return (
        weights.abs()
        .le(tolerance)
        .mean()
        .rename("zero_weight_rate")
    )


def turnover_summary(
    turnover: pd.Series,
) -> dict[str, float]:
    """Summarize portfolio turnover."""
    clean = turnover.dropna()

    return {
        "average_monthly_turnover": float(
            clean.mean()
        ),
        "median_monthly_turnover": float(
            clean.median()
        ),
        "maximum_monthly_turnover": float(
            clean.max()
        ),
        "total_turnover": float(
            clean.sum()
        ),
    }


def build_weight_diagnostics(
    weights: pd.DataFrame,
) -> pd.DataFrame:
    """Create an asset-level portfolio behavior report."""
    return pd.concat(
        [
            average_weights(weights),
            minimum_weights(weights),
            maximum_weights(weights),
            concentration_rate(weights),
            zero_weight_rate(weights),
        ],
        axis=1,
    )
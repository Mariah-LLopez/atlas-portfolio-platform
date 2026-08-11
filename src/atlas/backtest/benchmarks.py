from __future__ import annotations

import numpy as np
import pandas as pd


def constant_weight_portfolio_returns(
    returns: pd.DataFrame,
    weights: pd.Series,
) -> pd.Series:
    """Calculate returns for a constant-weight benchmark."""

    aligned_weights = weights.reindex(
        returns.columns
    )

    if aligned_weights.isna().any():
        missing = (
            aligned_weights[
                aligned_weights.isna()
            ]
            .index
            .tolist()
        )

        raise ValueError(
            f"Missing benchmark weights for assets: {missing}"
        )

    if not np.isclose(
        aligned_weights.sum(),
        1.0,
        atol=1e-8,
    ):
        raise ValueError(
            "Benchmark weights must sum to 1."
        )

    result = (
        returns
        .mul(
            aligned_weights,
            axis=1,
        )
        .sum(axis=1)
    )

    result.name = "benchmark_return"

    return result


def equal_weight_benchmark(
    returns: pd.DataFrame,
) -> pd.Series:
    """Equal-weight benchmark across all supplied assets."""

    weight = (
        1.0
        / len(returns.columns)
    )

    weights = pd.Series(
        weight,
        index=returns.columns,
        dtype=float,
    )

    result = constant_weight_portfolio_returns(
        returns,
        weights,
    )

    result.name = "equal_weight_return"

    return result


def sixty_forty_benchmark(
    returns: pd.DataFrame,
    equity_asset: str = "SPY",
    bond_asset: str = "IEF",
) -> pd.Series:
    """Simple 60/40 equity/Treasury proxy benchmark."""

    required = {
        equity_asset,
        bond_asset,
    }

    missing = required.difference(
        returns.columns
    )

    if missing:
        raise ValueError(
            f"Missing 60/40 benchmark assets: {sorted(missing)}"
        )

    benchmark_returns = returns[
        [
            equity_asset,
            bond_asset,
        ]
    ]

    weights = pd.Series(
        {
            equity_asset: 0.60,
            bond_asset: 0.40,
        },
        dtype=float,
    )

    result = constant_weight_portfolio_returns(
        benchmark_returns,
        weights,
    )

    result.name = "sixty_forty_return"

    return result
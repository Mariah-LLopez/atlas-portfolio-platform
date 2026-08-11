from __future__ import annotations

import cvxpy as cp
import numpy as np
import pandas as pd


class OptimizationError(RuntimeError):
    """Raised when the portfolio optimizer cannot produce a valid solution."""


def _make_covariance_psd(
    covariance: pd.DataFrame,
) -> np.ndarray:
    """Return a symmetric positive-semidefinite covariance matrix."""
    matrix = covariance.to_numpy(dtype=float)

    symmetric = (matrix + matrix.T) / 2.0

    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)

    clipped = np.clip(
        eigenvalues,
        1e-10,
        None,
    )

    return eigenvectors @ np.diag(clipped) @ eigenvectors.T


def optimize_portfolio(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    max_weights: pd.Series,
    *,
    cash_asset: str = "BIL",
    min_cash_weight: float = 0.02,
    equity_assets: list[str] | None = None,
    max_equity_weight: float | None = None,
    risk_aversion: float = 5.0,
) -> pd.Series:
    """Solve a long-only constrained mean-variance portfolio."""

    assets = expected_returns.index.tolist()

    if not assets:
        raise ValueError("Expected returns cannot be empty.")

    if risk_aversion <= 0:
        raise ValueError("risk_aversion must be positive.")

    if cash_asset not in assets:
        raise ValueError(
            f"Cash asset {cash_asset!r} is not in the asset universe."
        )

    if set(covariance.index) != set(assets):
        raise ValueError(
            "Covariance index does not match expected-return assets."
        )

    if set(covariance.columns) != set(assets):
        raise ValueError(
            "Covariance columns do not match expected-return assets."
        )

    covariance = covariance.reindex(
        index=assets,
        columns=assets,
    )

    caps = max_weights.reindex(assets)

    if caps.isna().any():
        missing = caps[caps.isna()].index.tolist()
        raise ValueError(
            f"Missing maximum weights for assets: {missing}"
        )

    if min_cash_weight < 0 or min_cash_weight > 1:
        raise ValueError(
            "min_cash_weight must be between 0 and 1."
        )

    mu = expected_returns.to_numpy(dtype=float)
    covariance_psd = _make_covariance_psd(covariance)

    weights = cp.Variable(len(assets))

    portfolio_return = mu @ weights

    portfolio_variance = cp.quad_form(
        weights,
        covariance_psd,
    )

    objective = cp.Maximize(
        portfolio_return
        - risk_aversion * portfolio_variance
    )

    constraints = [
        cp.sum(weights) == 1.0,
        weights >= 0.0,
        weights <= caps.to_numpy(dtype=float),
    ]

    cash_index = assets.index(cash_asset)

    constraints.append(
        weights[cash_index] >= min_cash_weight
    )

    if (
        equity_assets is not None
        and max_equity_weight is not None
    ):
        equity_indices = [
            assets.index(asset)
            for asset in equity_assets
            if asset in assets
        ]

        constraints.append(
            cp.sum(weights[equity_indices])
            <= max_equity_weight
        )

    problem = cp.Problem(
        objective,
        constraints,
    )

    problem.solve()

    if problem.status not in {
        cp.OPTIMAL,
        cp.OPTIMAL_INACCURATE,
    }:
        raise OptimizationError(
            f"Optimizer failed with status: {problem.status}"
        )

    result = pd.Series(
        np.asarray(weights.value).reshape(-1),
        index=assets,
        name="weight",
    )

    result[result.abs() < 1e-10] = 0.0

    return result
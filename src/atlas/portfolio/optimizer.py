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

    symmetric = (
        matrix + matrix.T
    ) / 2.0

    eigenvalues, eigenvectors = np.linalg.eigh(
        symmetric
    )

    clipped = np.clip(
        eigenvalues,
        1e-10,
        None,
    )

    return (
        eigenvectors
        @ np.diag(clipped)
        @ eigenvectors.T
    )


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
    previous_weights: pd.Series | None = None,
    max_turnover: float | None = None,
    turnover_penalty: float = 0.0,
) -> pd.Series:
    """Solve a constrained long-only mean-variance portfolio.

    Optional previous weights allow Atlas to penalize and/or
    constrain portfolio turnover.
    """

    assets = expected_returns.index.tolist()

    if not assets:
        raise ValueError(
            "Expected returns cannot be empty."
        )

    if risk_aversion <= 0:
        raise ValueError(
            "risk_aversion must be positive."
        )

    if turnover_penalty < 0:
        raise ValueError(
            "turnover_penalty cannot be negative."
        )

    if cash_asset not in assets:
        raise ValueError(
            f"Cash asset {cash_asset!r} "
            "is not in the asset universe."
        )

    if set(covariance.index) != set(assets):
        raise ValueError(
            "Covariance index does not match "
            "expected-return assets."
        )

    if set(covariance.columns) != set(assets):
        raise ValueError(
            "Covariance columns do not match "
            "expected-return assets."
        )

    covariance = covariance.reindex(
        index=assets,
        columns=assets,
    )

    caps = max_weights.reindex(
        assets
    )

    if caps.isna().any():
        missing = (
            caps[
                caps.isna()
            ]
            .index
            .tolist()
        )

        raise ValueError(
            f"Missing maximum weights for assets: "
            f"{missing}"
        )

    if (
        min_cash_weight < 0
        or min_cash_weight > 1
    ):
        raise ValueError(
            "min_cash_weight must be "
            "between 0 and 1."
        )

    if (
        max_turnover is not None
        and (
            max_turnover < 0
            or max_turnover > 1
        )
    ):
        raise ValueError(
            "max_turnover must be "
            "between 0 and 1."
        )

    previous = None

    if previous_weights is not None:
        previous = previous_weights.reindex(
            assets
        )

        if previous.isna().any():
            missing = (
                previous[
                    previous.isna()
                ]
                .index
                .tolist()
            )

            raise ValueError(
                "Missing previous weights for "
                f"assets: {missing}"
            )

        if not np.isclose(
            previous.sum(),
            1.0,
            atol=1e-6,
        ):
            raise ValueError(
                "Previous weights must sum to 1."
            )

        if (
            previous < -1e-8
        ).any():
            raise ValueError(
                "Previous weights cannot be negative."
            )

    elif (
        max_turnover is not None
        or turnover_penalty > 0
    ):
        raise ValueError(
            "previous_weights are required when "
            "using turnover controls."
        )

    mu = expected_returns.to_numpy(
        dtype=float
    )

    covariance_psd = (
        _make_covariance_psd(
            covariance
        )
    )

    weights = cp.Variable(
        len(assets)
    )

    portfolio_return = (
        mu @ weights
    )

    portfolio_variance = cp.quad_form(
        weights,
        covariance_psd,
    )

    objective_value = (
        portfolio_return
        - risk_aversion
        * portfolio_variance
    )

    turnover_expression = None

    if previous is not None:
        previous_array = previous.to_numpy(
            dtype=float
        )

        turnover_expression = (
            0.5
            * cp.norm1(
                weights
                - previous_array
            )
        )

        objective_value -= (
            turnover_penalty
            * turnover_expression
        )

    objective = cp.Maximize(
        objective_value
    )

    constraints = [
        cp.sum(weights) == 1.0,
        weights >= 0.0,
        weights
        <= caps.to_numpy(
            dtype=float
        ),
    ]

    cash_index = assets.index(
        cash_asset
    )

    constraints.append(
        weights[cash_index]
        >= min_cash_weight
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
            cp.sum(
                weights[
                    equity_indices
                ]
            )
            <= max_equity_weight
        )

    if (
        turnover_expression is not None
        and max_turnover is not None
    ):
        constraints.append(
            turnover_expression
            <= max_turnover
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
            "Optimizer failed with status: "
            f"{problem.status}"
        )

    result = pd.Series(
        np.asarray(
            weights.value
        ).reshape(-1),
        index=assets,
        name="weight",
        dtype=float,
    )

    result[
        result.abs() < 1e-10
    ] = 0.0

    return result
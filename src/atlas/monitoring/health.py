from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HealthCheck:
    name: str
    status: str
    detail: str


def check_portfolio_weights(
    weights: pd.Series,
    *,
    tolerance: float = 1e-6,
) -> HealthCheck:
    """Check that target portfolio weights form a valid long-only portfolio."""

    total = float(weights.sum())

    negative_count = int(
        (
            weights
            < -tolerance
        ).sum()
    )

    passed = (
        np.isclose(
            total,
            1.0,
            atol=tolerance,
        )
        and negative_count == 0
    )

    return HealthCheck(
        name="portfolio_weights",
        status=(
            "PASS"
            if passed
            else "FAIL"
        ),
        detail=(
            f"sum={total:.8f}, "
            f"negative_weights={negative_count}"
        ),
    )


def check_equity_limit(
    weights: pd.Series,
    *,
    equity_assets: list[str],
    maximum: float,
    tolerance: float = 1e-6,
) -> HealthCheck:
    """Check portfolio equity exposure against policy."""

    equity_weight = float(
        weights
        .reindex(
            equity_assets
        )
        .fillna(0.0)
        .sum()
    )

    passed = (
        equity_weight
        <= maximum
        + tolerance
    )

    return HealthCheck(
        name="equity_limit",
        status=(
            "PASS"
            if passed
            else "FAIL"
        ),
        detail=(
            f"equity={equity_weight:.4%}, "
            f"limit={maximum:.4%}"
        ),
    )


def check_cash_floor(
    weights: pd.Series,
    *,
    cash_asset: str,
    minimum: float,
    tolerance: float = 1e-6,
) -> HealthCheck:
    """Check minimum cash allocation."""

    if cash_asset not in weights.index:
        return HealthCheck(
            name="cash_floor",
            status="FAIL",
            detail=(
                f"{cash_asset} missing "
                "from portfolio"
            ),
        )

    cash_weight = float(
        weights.loc[
            cash_asset
        ]
    )

    passed = (
        cash_weight
        + tolerance
        >= minimum
    )

    return HealthCheck(
        name="cash_floor",
        status=(
            "PASS"
            if passed
            else "FAIL"
        ),
        detail=(
            f"cash={cash_weight:.4%}, "
            f"minimum={minimum:.4%}"
        ),
    )


def check_turnover_limit(
    turnover: pd.Series,
    *,
    maximum: float,
    tolerance: float = 1e-6,
) -> HealthCheck:
    """Check historical rebalances for turnover breaches."""

    clean = turnover.dropna()

    if clean.empty:
        return HealthCheck(
            name="turnover_limit",
            status="FAIL",
            detail="No turnover observations.",
        )

    maximum_observed = float(
        clean.max()
    )

    breach_count = int(
        (
            clean
            > maximum
            + tolerance
        ).sum()
    )

    passed = (
        breach_count == 0
    )

    return HealthCheck(
        name="turnover_limit",
        status=(
            "PASS"
            if passed
            else "FAIL"
        ),
        detail=(
            f"max={maximum_observed:.4%}, "
            f"limit={maximum:.4%}, "
            f"breaches={breach_count}"
        ),
    )


def check_attribution_reconciliation(
    reconciliation_error: float,
    *,
    tolerance: float = 1e-8,
) -> HealthCheck:
    """Check whether attribution reconciles to portfolio returns."""

    passed = (
        abs(
            reconciliation_error
        )
        <= tolerance
    )

    return HealthCheck(
        name="attribution_reconciliation",
        status=(
            "PASS"
            if passed
            else "FAIL"
        ),
        detail=(
            f"error="
            f"{reconciliation_error:.12f}, "
            f"tolerance={tolerance:.12f}"
        ),
    )


def overall_status(
    checks: list[HealthCheck],
) -> str:
    """Calculate overall system health."""

    statuses = {
        check.status
        for check in checks
    }

    if "FAIL" in statuses:
        return "FAILED"

    if "WARNING" in statuses:
        return "WARNING"

    return "HEALTHY"


def checks_to_records(
    checks: list[HealthCheck],
) -> list[dict]:
    """Convert health checks to serializable records."""

    return [
        asdict(check)
        for check in checks
    ]
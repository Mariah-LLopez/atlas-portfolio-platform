from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from atlas.config import load_yaml
from atlas.monitoring.health import (
    HealthCheck,
    check_attribution_reconciliation,
    check_cash_floor,
    check_equity_limit,
    check_portfolio_weights,
    check_turnover_limit,
    checks_to_records,
    overall_status,
)


DATA = Path("data/processed")


def file_check(
    name: str,
    path: Path,
) -> HealthCheck:
    """Check that a required production artifact exists."""

    exists = path.exists()

    return HealthCheck(
        name=name,
        status="PASS" if exists else "FAIL",
        detail=(
            f"Found {path}"
            if exists
            else f"Missing {path}"
        ),
    )


def main() -> None:
    print("Running Atlas model-health checks...")

    portfolio_config = load_yaml(
        "configs/portfolio.yaml"
    )

    portfolio_settings = portfolio_config[
        "portfolio"
    ]

    checks: list[HealthCheck] = []

    required_outputs = {
        "market_prices_output": (
            DATA / "market_prices.parquet"
        ),
        "macro_regimes_output": (
            DATA / "macro_regimes.parquet"
        ),
        "cma_output": (
            DATA
            / "cma_regime_adjusted.parquet"
        ),
        "optimized_weights_output": (
            DATA / "optimized_weights.parquet"
        ),
        "backtest_output": (
            DATA / "backtest_returns.parquet"
        ),
        "turnover_output": (
            DATA / "backtest_turnover.parquet"
        ),
        "attribution_output": (
            DATA
            / "attribution_summary.parquet"
        ),
        "attribution_report_output": (
            DATA
            / "attribution_report.json"
        ),
        "data_quality_output": (
            DATA
            / "data_quality_report.json"
        ),
    }

    for name, path in required_outputs.items():
        checks.append(
            file_check(
                name,
                path,
            )
        )

    # --------------------------------------------------------------
    # Data quality
    # --------------------------------------------------------------
    quality_path = (
        DATA
        / "data_quality_report.json"
    )

    if quality_path.exists():
        quality_report = json.loads(
            quality_path.read_text(
                encoding="utf-8"
            )
        )

        data_quality_passed = bool(
            quality_report.get(
                "overall_passed",
                False,
            )
        )

        checks.append(
            HealthCheck(
                name="market_data_quality",
                status=(
                    "PASS"
                    if data_quality_passed
                    else "FAIL"
                ),
                detail=(
                    "All configured market-data "
                    "quality checks passed."
                    if data_quality_passed
                    else (
                        "One or more market-data "
                        "quality checks failed."
                    )
                ),
            )
        )

    # --------------------------------------------------------------
    # Current optimized portfolio
    # --------------------------------------------------------------
    weights_path = (
        DATA
        / "optimized_weights.parquet"
    )

    if weights_path.exists():
        weight_frame = pd.read_parquet(
            weights_path
        )

        weights = (
            weight_frame[
                "weight"
            ]
            .astype(float)
        )

        checks.append(
            check_portfolio_weights(
                weights
            )
        )

        checks.append(
            check_equity_limit(
                weights,
                equity_assets=[
                    "SPY",
                    "VXUS",
                ],
                maximum=float(
                    portfolio_settings[
                        "max_equity_weight"
                    ]
                ),
            )
        )

        checks.append(
            check_cash_floor(
                weights,
                cash_asset="BIL",
                minimum=float(
                    portfolio_settings[
                        "min_cash_weight"
                    ]
                ),
            )
        )

    # --------------------------------------------------------------
    # Historical turnover
    # --------------------------------------------------------------
    turnover_path = (
        DATA
        / "backtest_turnover.parquet"
    )

    if turnover_path.exists():
        turnover_frame = pd.read_parquet(
            turnover_path
        )

        turnover = (
            turnover_frame[
                "turnover"
            ]
            .astype(float)
        )

        checks.append(
            check_turnover_limit(
                turnover,
                maximum=float(
                    portfolio_settings[
                        "max_turnover_per_rebalance"
                    ]
                ),
            )
        )

    # --------------------------------------------------------------
    # Attribution reconciliation
    # --------------------------------------------------------------
    attribution_report_path = (
        DATA
        / "attribution_report.json"
    )

    if attribution_report_path.exists():
        attribution_report = json.loads(
            attribution_report_path.read_text(
                encoding="utf-8"
            )
        )

        reconciliation = float(
            attribution_report[
                "maximum_daily_reconciliation_error"
            ]
        )

        checks.append(
            check_attribution_reconciliation(
                reconciliation
            )
        )

    # --------------------------------------------------------------
    # Overall health
    # --------------------------------------------------------------
    status = overall_status(
        checks
    )

    report = {
        "generated_at_utc": (
            datetime.now(UTC)
            .isoformat()
        ),
        "overall_status": status,
        "check_count": len(checks),
        "passed_checks": sum(
            check.status == "PASS"
            for check in checks
        ),
        "failed_checks": sum(
            check.status == "FAIL"
            for check in checks
        ),
        "warning_checks": sum(
            check.status == "WARNING"
            for check in checks
        ),
        "checks": checks_to_records(
            checks
        ),
    }

    output = (
        DATA
        / "model_health.json"
    )

    output.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("ATLAS MODEL HEALTH")
    print("=" * 60)

    print(
        f"\nOverall Status: {status}"
    )

    print(
        f"Checks passed: "
        f"{report['passed_checks']}"
        f"/{report['check_count']}"
    )

    print()

    for check in checks:
        symbol = (
            "✓"
            if check.status == "PASS"
            else "✗"
        )

        print(
            f"{symbol} "
            f"{check.name}: "
            f"{check.status}"
        )

        print(
            f"    {check.detail}"
        )

    print()
    print(
        f"Saved: {output}"
    )

    if status != "HEALTHY":
        raise SystemExit(
            "Atlas model health is not HEALTHY."
        )


if __name__ == "__main__":
    main()
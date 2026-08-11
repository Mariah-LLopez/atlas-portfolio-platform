from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import timedelta

import pandas as pd


@dataclass(frozen=True)
class QualityCheck:
    name: str
    passed: bool
    detail: str


def check_nonempty(frame: pd.DataFrame) -> QualityCheck:
    return QualityCheck("nonempty", not frame.empty, f"{len(frame):,} rows")


def check_unique_index(frame: pd.DataFrame) -> QualityCheck:
    duplicates = int(frame.index.duplicated().sum())
    return QualityCheck("unique_index", duplicates == 0, f"{duplicates} duplicate index values")


def check_monotonic_index(frame: pd.DataFrame) -> QualityCheck:
    passed = frame.index.is_monotonic_increasing
    return QualityCheck(
        "monotonic_index",
        bool(passed),
        "index is increasing" if passed else "index is not increasing",
    )


def check_missing_ratio(frame: pd.DataFrame, max_ratio: float = 0.05) -> QualityCheck:
    ratio = 1.0 if frame.empty else float(frame.isna().sum().sum() / frame.size)
    return QualityCheck(
        "missing_ratio",
        ratio <= max_ratio,
        f"{ratio:.2%} missing; threshold {max_ratio:.2%}",
    )


def check_positive_prices(frame: pd.DataFrame) -> QualityCheck:
    values = frame.stack(future_stack=True).dropna()
    bad = int((values <= 0).sum())
    return QualityCheck(
        "positive_prices",
        bad == 0,
        f"{bad} non-positive price observations",
    )


def check_staleness(
    frame: pd.DataFrame,
    as_of: pd.Timestamp | None = None,
    max_age_days: int = 7,
) -> QualityCheck:
    if frame.empty:
        return QualityCheck("staleness", False, "frame is empty")
    latest = pd.Timestamp(frame.dropna(how="all").index.max()).normalize()
    reference = (as_of or pd.Timestamp.utcnow()).tz_localize(None).normalize()
    age = reference - latest
    passed = age <= timedelta(days=max_age_days)
    return QualityCheck(
        "staleness",
        bool(passed),
        f"latest={latest.date()}, age={age.days} days, threshold={max_age_days}",
    )


def validate_market_prices(
    prices: pd.DataFrame,
    *,
    as_of: pd.Timestamp | None = None,
    max_missing_ratio: float = 0.05,
    max_age_days: int = 7,
) -> list[QualityCheck]:
    return [
        check_nonempty(prices),
        check_unique_index(prices),
        check_monotonic_index(prices),
        check_missing_ratio(prices, max_ratio=max_missing_ratio),
        check_positive_prices(prices),
        check_staleness(prices, as_of=as_of, max_age_days=max_age_days),
    ]


def checks_to_dict(checks: list[QualityCheck]) -> list[dict]:
    return [asdict(check) for check in checks]

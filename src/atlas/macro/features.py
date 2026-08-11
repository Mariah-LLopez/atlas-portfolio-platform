from __future__ import annotations

import pandas as pd

REQUIRED_MACRO_COLUMNS = {
    "CPIAUCSL",
    "INDPRO",
    "FEDFUNDS",
    "DGS2",
    "DGS10",
}


def to_monthly_macro(macro: pd.DataFrame) -> pd.DataFrame:
    """Convert mixed-frequency FRED data to month-end observations."""
    missing = REQUIRED_MACRO_COLUMNS.difference(macro.columns)

    if missing:
        raise ValueError(
            f"Missing required macro columns: {sorted(missing)}"
        )

    monthly = macro.resample("ME").last()
    return monthly


def build_macro_features(macro: pd.DataFrame) -> pd.DataFrame:
    """Create transparent macro features used by the regime model."""
    monthly = to_monthly_macro(macro)

    features = pd.DataFrame(index=monthly.index)

    # Year-over-year inflation.
    features["inflation_yoy"] = (
        monthly["CPIAUCSL"].pct_change(12, fill_method=None) * 100
    )

    # Year-over-year industrial-production growth.
    features["growth_yoy"] = (
        monthly["INDPRO"].pct_change(12, fill_method=None) * 100
    )

    # Change over the last three months.
    features["inflation_trend_3m"] = features["inflation_yoy"].diff(3)
    features["growth_trend_3m"] = features["growth_yoy"].diff(3)

    # Treasury yield-curve slope.
    features["yield_curve_10y_2y"] = (
        monthly["DGS10"] - monthly["DGS2"]
    )

    # Direction of monetary policy.
    features["fed_funds_change_3m"] = monthly["FEDFUNDS"].diff(3)

    return features


def classify_regimes(features: pd.DataFrame) -> pd.Series:
    """Classify each month into one of four directional macro regimes."""
    required = {"inflation_trend_3m", "growth_trend_3m"}

    missing = required.difference(features.columns)

    if missing:
        raise ValueError(
            f"Missing required regime features: {sorted(missing)}"
        )

    regimes = pd.Series(
        pd.NA,
        index=features.index,
        dtype="string",
        name="macro_regime",
    )

    growth_up = features["growth_trend_3m"] >= 0
    growth_down = features["growth_trend_3m"] < 0

    inflation_up = features["inflation_trend_3m"] > 0
    inflation_down = features["inflation_trend_3m"] <= 0

    regimes.loc[growth_up & inflation_down] = "expansion"
    regimes.loc[growth_up & inflation_up] = "inflationary_growth"
    regimes.loc[growth_down & inflation_down] = "slowdown"
    regimes.loc[growth_down & inflation_up] = "stagflation"

    return regimes
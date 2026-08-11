from __future__ import annotations

import pandas as pd

REGIME_TILTS = {
    "expansion": {
        "SPY": 0.015,
        "VXUS": 0.010,
        "IEF": -0.005,
        "LQD": 0.005,
        "VNQ": 0.005,
        "GLD": -0.005,
        "BIL": -0.005,
    },
    "inflationary_growth": {
        "SPY": 0.005,
        "VXUS": 0.005,
        "IEF": -0.010,
        "LQD": -0.005,
        "VNQ": 0.000,
        "GLD": 0.010,
        "BIL": 0.000,
    },
    "slowdown": {
        "SPY": -0.010,
        "VXUS": -0.010,
        "IEF": 0.010,
        "LQD": -0.005,
        "VNQ": -0.005,
        "GLD": 0.005,
        "BIL": 0.005,
    },
    "stagflation": {
        "SPY": -0.015,
        "VXUS": -0.010,
        "IEF": -0.005,
        "LQD": -0.010,
        "VNQ": -0.005,
        "GLD": 0.015,
        "BIL": 0.010,
    },
}


def get_regime_tilts(
    regime: str,
    assets: list[str],
) -> pd.Series:
    """Return demonstration annual expected-return tilts for a macro regime."""
    if regime not in REGIME_TILTS:
        raise ValueError(f"Unknown macro regime: {regime}")

    configured = REGIME_TILTS[regime]
    missing = set(assets).difference(configured)

    if missing:
        raise ValueError(
            f"No macro tilt configured for assets: {sorted(missing)}"
        )

    return pd.Series(
        {asset: configured[asset] for asset in assets},
        name="macro_tilt",
        dtype=float,
    )


def apply_regime_tilts(
    expected_returns: pd.Series,
    regime: str,
) -> pd.DataFrame:
    """Apply transparent macro tilts to baseline expected returns."""
    tilts = get_regime_tilts(
        regime,
        expected_returns.index.tolist(),
    )

    result = pd.DataFrame(
        {
            "base_expected_return": expected_returns,
            "macro_tilt": tilts,
        }
    )

    result["regime_adjusted_expected_return"] = (
        result["base_expected_return"] + result["macro_tilt"]
    )

    return result
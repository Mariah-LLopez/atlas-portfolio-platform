import numpy as np
import pandas as pd
import pytest

from atlas.macro.tilts import (
    apply_regime_tilts,
    get_regime_tilts,
)


def test_stagflation_favors_gold_over_equity():
    tilts = get_regime_tilts(
        "stagflation",
        ["SPY", "GLD"],
    )

    assert tilts["GLD"] > tilts["SPY"]


def test_expansion_favors_equity_over_cash():
    tilts = get_regime_tilts(
        "expansion",
        ["SPY", "BIL"],
    )

    assert tilts["SPY"] > tilts["BIL"]


def test_unknown_regime_fails():
    with pytest.raises(ValueError):
        get_regime_tilts(
            "unknown_regime",
            ["SPY"],
        )


def test_adjusted_return_equals_base_plus_tilt():
    expected_returns = pd.Series(
        {
            "SPY": 0.07,
            "GLD": 0.04,
        }
    )

    result = apply_regime_tilts(
        expected_returns,
        "stagflation",
    )

    assert np.isclose(
        result.loc["SPY", "regime_adjusted_expected_return"],
        0.055,
    )

    assert np.isclose(
        result.loc["GLD", "regime_adjusted_expected_return"],
        0.055,
    )
    
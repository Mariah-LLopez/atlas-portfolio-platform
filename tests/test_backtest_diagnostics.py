import numpy as np
import pandas as pd

from atlas.backtest.diagnostics import (
    build_weight_diagnostics,
    turnover_summary,
)


def test_weight_diagnostics():
    weights = pd.DataFrame(
        {
            "SPY": [0.40, 0.20],
            "BIL": [0.60, 0.80],
        }
    )

    diagnostics = build_weight_diagnostics(
        weights
    )

    assert np.isclose(
        diagnostics.loc[
            "SPY",
            "average_weight",
        ],
        0.30,
    )

    assert np.isclose(
        diagnostics.loc[
            "SPY",
            "maximum_weight",
        ],
        0.40,
    )


def test_turnover_summary():
    turnover = pd.Series(
        [0.0, 0.10, 0.20]
    )

    summary = turnover_summary(
        turnover
    )

    assert np.isclose(
        summary[
            "average_monthly_turnover"
        ],
        0.10,
    )

    assert np.isclose(
        summary[
            "maximum_monthly_turnover"
        ],
        0.20,
    )
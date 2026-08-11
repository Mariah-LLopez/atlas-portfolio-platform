from __future__ import annotations

import pandas as pd


def equal_weight(tickers: list[str]) -> pd.Series:
    if not tickers:
        raise ValueError("At least one ticker is required.")
    weight = 1.0 / len(tickers)
    return pd.Series(weight, index=tickers, name="weight", dtype=float)

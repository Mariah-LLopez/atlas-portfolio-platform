from __future__ import annotations

import pandas as pd


def monthly_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Convert daily prices to month-end observed prices."""
    return prices.resample("ME").last()


def momentum_12_1(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate 12-month momentum excluding the most recent month."""
    monthly = monthly_prices(prices)
    return monthly.shift(1) / monthly.shift(12) - 1.0


def cross_sectional_zscore(signal: pd.DataFrame) -> pd.DataFrame:
    """Normalize each date's signal across assets."""
    mean = signal.mean(axis=1)
    std = signal.std(axis=1, ddof=0).replace(0.0, pd.NA)
    return signal.sub(mean, axis=0).div(std, axis=0)

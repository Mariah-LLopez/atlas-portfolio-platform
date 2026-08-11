from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_annualized_volatility(
    returns: pd.DataFrame,
    window: int = 63,
    periods_per_year: int = 252,
) -> pd.DataFrame:
    return returns.rolling(window=window, min_periods=window).std() * np.sqrt(periods_per_year)

from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_historical_return(
    returns: pd.DataFrame,
    periods_per_year: int = 252,
    years: int = 5,
) -> pd.Series:
    """Arithmetic annualized mean over the trailing research window."""
    window = returns.tail(periods_per_year * years)
    return window.mean() * periods_per_year


def annualized_covariance(
    returns: pd.DataFrame,
    periods_per_year: int = 252,
    years: int = 5,
) -> pd.DataFrame:
    window = returns.tail(periods_per_year * years)
    return window.cov() * periods_per_year


def demonstration_expected_returns(
    returns: pd.DataFrame,
    momentum_z: pd.Series,
    *,
    years: int = 5,
    momentum_tilt: float = 0.02,
    periods_per_year: int = 252,
) -> pd.Series:
    """Blend historical expected returns with a transparent momentum tilt."""
    base = annualized_historical_return(
        returns,
        periods_per_year=periods_per_year,
        years=years,
    )
    tilt = momentum_z.reindex(base.index).fillna(0.0) * momentum_tilt
    return (base + tilt).rename("expected_return")


def expected_volatility(covariance: pd.DataFrame) -> pd.Series:
    return pd.Series(
        np.sqrt(np.diag(covariance)),
        index=covariance.index,
        name="expected_volatility",
    )

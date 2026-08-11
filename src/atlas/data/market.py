from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf


class MarketDataError(RuntimeError):
    """Raised when market data cannot be retrieved or normalized."""


def download_adjusted_close(
    tickers: list[str],
    start: str,
    end: str | None = None,
) -> pd.DataFrame:
    """Download daily adjusted market prices for the configured research universe."""
    if not tickers:
        raise ValueError("At least one ticker is required.")

    raw = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=True,
    )

    if raw.empty:
        raise MarketDataError("Market-data download returned no rows.")

    if isinstance(raw.columns, pd.MultiIndex):
        level0 = raw.columns.get_level_values(0)
        if "Close" not in level0:
            raise MarketDataError("Expected a Close field in yfinance output.")
        prices = raw["Close"].copy()
    else:
        if "Close" not in raw.columns:
            raise MarketDataError("Expected a Close field in yfinance output.")
        prices = raw[["Close"]].copy()
        if len(tickers) == 1:
            prices.columns = tickers

    prices.index = pd.to_datetime(prices.index)
    prices = prices.sort_index()
    prices = prices.reindex(columns=tickers)
    return prices.astype(float)


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate simple daily returns."""
    return prices.pct_change(fill_method=None)


def save_parquet(frame: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path)

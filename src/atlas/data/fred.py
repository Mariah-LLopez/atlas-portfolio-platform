from __future__ import annotations

import os
from collections.abc import Iterable

import pandas as pd
import requests


FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


class FredDataError(RuntimeError):
    """Raised when FRED data cannot be retrieved or parsed."""


def fetch_series(
    series_id: str,
    api_key: str,
    observation_start: str = "2015-01-01",
    timeout: int = 30,
) -> pd.Series:
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": observation_start,
    }

    response = requests.get(FRED_OBSERVATIONS_URL, params=params, timeout=timeout)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise FredDataError(f"FRED request failed for {series_id}: {exc}") from exc

    payload = response.json()
    if "observations" not in payload:
        raise FredDataError(f"Unexpected FRED payload for {series_id}.")

    rows = []
    for item in payload["observations"]:
        value = item["value"]
        parsed = float("nan") if value == "." else float(value)
        rows.append((pd.Timestamp(item["date"]), parsed))

    return pd.Series(
        data=[value for _, value in rows],
        index=[date for date, _ in rows],
        name=series_id,
        dtype=float,
    ).sort_index()


def fetch_macro_frame(
    series_ids: Iterable[str],
    observation_start: str = "2015-01-01",
    api_key: str | None = None,
) -> pd.DataFrame:
    key = api_key or os.getenv("FRED_API_KEY")
    if not key or key == "replace_me":
        raise FredDataError(
            "FRED_API_KEY is missing. Copy .env.example to .env and set your API key."
        )

    series = [
        fetch_series(series_id, api_key=key, observation_start=observation_start)
        for series_id in series_ids
    ]
    return pd.concat(series, axis=1).sort_index()

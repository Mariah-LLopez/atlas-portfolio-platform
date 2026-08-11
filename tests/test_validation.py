import pandas as pd

from atlas.data.validation import (
    check_missing_ratio,
    check_positive_prices,
    check_unique_index,
)


def test_unique_index_passes_for_unique_dates():
    frame = pd.DataFrame(
        {"SPY": [100.0, 101.0]},
        index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
    )
    assert check_unique_index(frame).passed


def test_positive_prices_rejects_zero():
    frame = pd.DataFrame(
        {"SPY": [100.0, 0.0]},
        index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
    )
    assert not check_positive_prices(frame).passed


def test_missing_ratio_enforces_threshold():
    frame = pd.DataFrame({"A": [1.0, None], "B": [1.0, 2.0]})
    assert not check_missing_ratio(frame, max_ratio=0.20).passed

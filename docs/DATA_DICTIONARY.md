# Atlas Data Dictionary

## Market prices

**Dataset:** `data/processed/market_prices.parquet`

Index:
- Trading date

Columns:
- One column per configured ETF ticker

Definition:
- Adjusted daily closing price returned by the market-data adapter.

## Market returns

**Dataset:** `data/processed/market_returns.parquet`

Definition:
- Simple return: `P_t / P_(t-1) - 1`.

## Macro

**Dataset:** `data/processed/macro.parquet`

Columns:
- `CPIAUCSL`
- `UNRATE`
- `INDPRO`
- `FEDFUNDS`
- `DGS2`
- `DGS10`

Important:
- FRED observations can be revised.
- Stage 1 uses currently available historical observations.
- A later milestone will add vintage-aware / point-in-time macro data.

## Momentum

**Dataset:** `momentum.parquet`

Definition:
- 12-1 momentum: month-end price at `t-1` divided by month-end price at `t-12`, minus one.

## Volatility

**Dataset:** `volatility.parquet`

Definition:
- Rolling standard deviation of daily simple returns multiplied by square root of 252.

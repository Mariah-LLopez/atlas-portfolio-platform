# Atlas — Multi-Asset Portfolio Research & Production Platform

Atlas is a portfolio project that demonstrates how a quantitative investment idea can move from
research notebook to production-style software.

## Stage 1: Research foundation

This starter repository implements:

- A configurable 7-asset multi-asset universe
- Market data ingestion through `yfinance`
- Macro data ingestion through the official FRED API
- Parquet-based processed data storage
- Data-quality checks
- 12-1 momentum
- Rolling annualized volatility
- Cross-sectional z-scores
- A simple demonstration Capital Market Assumption (CMA) engine
- Equal-weight baseline portfolio construction
- Unit tests
- GitHub Actions CI
- Documentation templates for model governance and AI-assisted engineering

## Asset universe

| Ticker | Sleeve | Role |
|---|---|---|
| SPY | US Equity | Growth |
| VXUS | International Equity | Diversification |
| IEF | US Treasuries | Defensive duration |
| LQD | Investment Grade Credit | Income / credit |
| VNQ | REITs | Real assets |
| GLD | Gold | Inflation / crisis diversifier |
| BIL | T-Bills | Cash proxy |

These ETFs are research proxies, not investment recommendations.

## Macro universe

| FRED ID | Meaning | Transformation used later |
|---|---|---|
| CPIAUCSL | CPI | 12-month inflation |
| UNRATE | Unemployment rate | level / change |
| INDPRO | Industrial production | 12-month growth |
| FEDFUNDS | Effective Fed funds rate | level / change |
| DGS2 | 2-year Treasury yield | month-end level |
| DGS10 | 10-year Treasury yield | month-end level |

Yield-curve slope will be `DGS10 - DGS2`.

## Repository layout

```text
atlas-portfolio-platform/
├── configs/
│   ├── assets.yaml
│   ├── macro.yaml
│   └── portfolio.yaml
├── data/
│   ├── raw/.gitkeep
│   ├── processed/.gitkeep
│   └── sample/.gitkeep
├── docs/
│   ├── AI_ENGINEERING_LOG.md
│   ├── DATA_DICTIONARY.md
│   ├── MODEL_SPECIFICATION.md
│   └── STAGE_1_ACCEPTANCE_CRITERIA.md
├── notebooks/
│   └── README.md
├── scripts/
│   ├── generate_sample_data.py
│   └── run_stage1.py
├── src/atlas/
│   ├── config.py
│   ├── data/
│   │   ├── fred.py
│   │   ├── market.py
│   │   └── validation.py
│   ├── cma/
│   │   └── assumptions.py
│   ├── portfolio/
│   │   └── baseline.py
│   └── signals/
│       ├── momentum.py
│       └── risk.py
├── tests/
├── .github/workflows/test.yml
├── .env.example
├── .gitignore
└── pyproject.toml
```

## Setup

Use Python 3.11+.

```bash
python -m venv .venv
```

Activate it.

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install the project:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Copy the environment template:

**Windows**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux**

```bash
cp .env.example .env
```

Add your FRED API key to `.env`.

## Run Stage 1

```bash
python scripts/run_stage1.py
```

Expected outputs:

```text
data/processed/market_prices.parquet
data/processed/market_returns.parquet
data/processed/macro.parquet
data/processed/momentum.parquet
data/processed/momentum_zscore.parquet
data/processed/volatility.parquet
data/processed/cma_expected_returns.parquet
data/processed/cma_covariance.parquet
data/processed/baseline_weights.parquet
data/processed/data_quality_report.json
```

## Run tests

```bash
pytest
```

## First GitHub milestone

Tag the first clean release:

```text
v0.1.0-research-foundation
```

The goal is not to claim that this model manages real institutional capital. The goal is to show
production-oriented quantitative engineering: reproducible data, explicit transformations,
validation, modular code, tests, documentation, and a clear path from research to deployment.

## Research caveat

`yfinance` is convenient for a portfolio demonstration but is not an institutional market-data
vendor. Atlas deliberately isolates market-data ingestion behind a module so a production source
could be substituted later without rewriting the signal, CMA, or portfolio layers.

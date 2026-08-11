# Atlas Model Specification — v0.1

## 1. Purpose

Atlas is an educational, production-style multi-asset research platform demonstrating the
engineering lifecycle for systematic asset-allocation research.

## 2. Investment hypothesis

Medium-term price momentum may contain useful information about relative asset performance.
Risk estimates can be used to prevent a signal from being interpreted independently of the
uncertainty associated with each asset.

Later versions add macro-regime conditioning and constrained portfolio optimization.

## 3. Asset universe

Seven liquid ETF proxies represent major multi-asset sleeves:
US equity, international equity, US Treasuries, investment-grade credit, REITs, gold, and T-bills.

## 4. Data dependencies

### Market
Adjusted daily ETF prices through a replaceable market-data adapter.

### Macro
FRED series for inflation, unemployment, industrial production, effective Fed funds,
and 2-year / 10-year Treasury yields.

## 5. Signals

### 12-1 momentum

At month `t`:

`momentum_t = price_(t-1) / price_(t-12) - 1`

### Risk

63-trading-day realized volatility:

`vol_t = std(daily returns over 63 observations) * sqrt(252)`

## 6. Demonstration CMA

Stage 1 expected return is:

`trailing annualized arithmetic mean + 0.02 * momentum_z_score`

This is intentionally simple and transparent. It is not presented as an institutional expected
return forecast.

Covariance is the annualized trailing historical covariance matrix.

## 7. Baseline portfolio

Equal weight across all configured assets.

## 8. Controls

Stage 1 blocks successful completion when required market data fail defined quality checks.

## 9. Testing

Tests cover:
- data-quality controls
- momentum timing
- z-score behavior
- volatility
- CMA tilt direction
- covariance dimensions
- portfolio weight invariants

## 10. Known limitations

- ETF histories differ by inception date.
- `yfinance` is appropriate for a demonstration, not an institutional feed.
- FRED macro history can contain revised data; point-in-time vintage handling is not yet implemented.
- No transaction costs, optimizer, execution model, or live holdings are included in v0.1.
- No claim is made that historical performance will predict future performance.

## 11. Planned versions

### v0.2
Macro feature engineering and regime model.

### v0.3
CVXPY constrained optimizer, turnover penalty, and risk constraints.

### v0.4
Walk-forward backtester, transaction costs, and benchmark comparisons.

### v0.5
Holdings, rebalance orders, and attribution.

### v0.6
Monitoring, logging, run manifests, and Streamlit dashboard.

### v0.7
AI research assistant, commentary generation, meeting-prep workflow, and AI engineering review log.

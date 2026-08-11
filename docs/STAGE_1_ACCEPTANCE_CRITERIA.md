# Stage 1 Acceptance Criteria

Stage 1 is complete when all of the following are true.

## Data ingestion
- [ ] All seven configured ETFs download successfully.
- [ ] Prices are stored as Parquet.
- [ ] Daily simple returns are derived from prices.
- [ ] Six configured FRED series download successfully.
- [ ] Macro data are stored separately from market data.

## Quality control
- [ ] Empty datasets fail.
- [ ] Duplicate dates fail.
- [ ] Non-monotonic date indexes fail.
- [ ] Excessive missing observations fail.
- [ ] Non-positive prices fail.
- [ ] Stale market data fail.
- [ ] The run emits a machine-readable quality report.

## Research outputs
- [ ] 12-1 momentum is calculated monthly.
- [ ] Cross-sectional momentum z-scores are calculated.
- [ ] 63-day annualized volatility is calculated.
- [ ] Historical annualized covariance is calculated.
- [ ] Demonstration expected returns are generated.
- [ ] Equal-weight baseline weights sum to 1 within numerical tolerance.

## Engineering
- [ ] `pytest` passes locally.
- [ ] `ruff check` passes locally.
- [ ] GitHub Actions passes.
- [ ] Secrets are excluded from Git.
- [ ] Downloaded datasets are excluded from Git.
- [ ] Research logic lives under `src/atlas`, not only in notebooks.

## Portfolio evidence

Capture screenshots of:
1. Passing test suite.
2. Green GitHub Actions workflow.
3. Stage 1 terminal output.
4. Processed-data directory.
5. A short GitHub pull request describing one change and its tests.

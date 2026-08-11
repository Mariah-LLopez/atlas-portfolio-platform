from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from atlas.cma.assumptions import (
    annualized_covariance,
    demonstration_expected_returns,
    expected_volatility,
)
from atlas.config import asset_tickers, load_yaml
from atlas.data.fred import fetch_macro_frame
from atlas.data.market import calculate_returns, download_adjusted_close, save_parquet
from atlas.data.validation import checks_to_dict, validate_market_prices
from atlas.macro.features import build_macro_features, classify_regimes
from atlas.portfolio.baseline import equal_weight
from atlas.signals.momentum import cross_sectional_zscore, momentum_12_1
from atlas.signals.risk import rolling_annualized_volatility

OUTPUT = Path("data/processed")


def main() -> None:
    load_dotenv()

    assets = asset_tickers()
    portfolio_config = load_yaml("configs/portfolio.yaml")
    macro_config = load_yaml("configs/macro.yaml")
    research = portfolio_config["research"]

    print("1/7 Downloading market data...")
    prices = download_adjusted_close(assets, start=research["start_date"])
    checks = validate_market_prices(prices)

    failed = [check for check in checks if not check.passed]
    if failed:
        details = "; ".join(f"{check.name}: {check.detail}" for check in failed)
        raise RuntimeError(f"Market data failed quality control: {details}")

    save_parquet(prices, OUTPUT / "market_prices.parquet")
    returns = calculate_returns(prices)
    save_parquet(returns, OUTPUT / "market_returns.parquet")

    print("2/7 Downloading macro data...")
    macro = fetch_macro_frame(
        macro_config["series"].keys(),
        observation_start=research["start_date"],
    )
    save_parquet(macro, OUTPUT / "macro.parquet")

    print("Building macro features and regimes...")
    macro_features = build_macro_features(macro)
    macro_regimes = classify_regimes(macro_features)

    save_parquet(
        macro_features,
        OUTPUT / "macro_features.parquet",
    )

    save_parquet(
        macro_regimes.to_frame(),
        OUTPUT / "macro_regimes.parquet",
    )

    print("3/7 Calculating momentum...")
    momentum = momentum_12_1(prices)
    momentum_z = cross_sectional_zscore(momentum)
    save_parquet(momentum, OUTPUT / "momentum.parquet")
    save_parquet(momentum_z, OUTPUT / "momentum_zscore.parquet")

    print("4/7 Calculating volatility...")
    volatility = rolling_annualized_volatility(
        returns,
        window=int(research["volatility_window_days"]),
        periods_per_year=int(research["annualization_factor"]),
    )
    save_parquet(volatility, OUTPUT / "volatility.parquet")

    print("5/7 Building demonstration CMAs...")
    latest_momentum_z = momentum_z.dropna(how="all").iloc[-1]
    expected_returns = demonstration_expected_returns(
        returns,
        latest_momentum_z,
        years=int(research["cma_history_years"]),
        momentum_tilt=float(research["cma_momentum_tilt"]),
        periods_per_year=int(research["annualization_factor"]),
    )
    covariance = annualized_covariance(
        returns,
        years=int(research["cma_history_years"]),
        periods_per_year=int(research["annualization_factor"]),
    )
    cma = pd.concat(
        [expected_returns, expected_volatility(covariance)],
        axis=1,
    )
    save_parquet(cma, OUTPUT / "cma_expected_returns.parquet")
    save_parquet(covariance, OUTPUT / "cma_covariance.parquet")

    print("6/7 Building equal-weight baseline...")
    weights = equal_weight(assets).to_frame()
    save_parquet(weights, OUTPUT / "baseline_weights.parquet")

    print("7/7 Writing quality report...")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {
        "overall_passed": all(check.passed for check in checks),
        "checks": checks_to_dict(checks),
    }
    (OUTPUT / "data_quality_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nStage 1 complete.")
    print(f"Latest market date: {prices.index.max().date()}")
    print(f"Assets: {', '.join(assets)}")
    print("\nLatest demonstration CMA:")
    print(cma.round(4).to_string())
    print("\nBaseline weights:")
    print(weights.round(4).to_string())


if __name__ == "__main__":
    main()

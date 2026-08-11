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
from atlas.macro.tilts import apply_regime_tilts
from atlas.portfolio.baseline import equal_weight
from atlas.portfolio.optimizer import optimize_portfolio
from atlas.signals.momentum import cross_sectional_zscore, momentum_12_1
from atlas.signals.risk import rolling_annualized_volatility

OUTPUT = Path("data/processed")


def main() -> None:
    load_dotenv()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    assets = asset_tickers()

    portfolio_config = load_yaml("configs/portfolio.yaml")
    asset_config = load_yaml("configs/assets.yaml")
    macro_config = load_yaml("configs/macro.yaml")

    portfolio_settings = portfolio_config["portfolio"]
    research = portfolio_config["research"]

    # ------------------------------------------------------------------
    # 1. Market data
    # ------------------------------------------------------------------
    print("1/7 Downloading market data...")

    prices = download_adjusted_close(
        assets,
        start=research["start_date"],
    )

    checks = validate_market_prices(prices)

    failed = [
        check
        for check in checks
        if not check.passed
    ]

    if failed:
        details = "; ".join(
            f"{check.name}: {check.detail}"
            for check in failed
        )
        raise RuntimeError(
            f"Market data failed quality control: {details}"
        )

    save_parquet(
        prices,
        OUTPUT / "market_prices.parquet",
    )

    returns = calculate_returns(prices)

    save_parquet(
        returns,
        OUTPUT / "market_returns.parquet",
    )

    # ------------------------------------------------------------------
    # 2. Macro data and regime engine
    # ------------------------------------------------------------------
    print("2/7 Downloading macro data...")

    macro = fetch_macro_frame(
        macro_config["series"].keys(),
        observation_start=research["start_date"],
    )

    save_parquet(
        macro,
        OUTPUT / "macro.parquet",
    )

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

    # ------------------------------------------------------------------
    # 3. Momentum
    # ------------------------------------------------------------------
    print("3/7 Calculating momentum...")

    momentum = momentum_12_1(prices)

    momentum_z = cross_sectional_zscore(
        momentum
    )

    save_parquet(
        momentum,
        OUTPUT / "momentum.parquet",
    )

    save_parquet(
        momentum_z,
        OUTPUT / "momentum_zscore.parquet",
    )

    # ------------------------------------------------------------------
    # 4. Risk
    # ------------------------------------------------------------------
    print("4/7 Calculating volatility...")

    volatility = rolling_annualized_volatility(
        returns,
        window=int(
            research["volatility_window_days"]
        ),
        periods_per_year=int(
            research["annualization_factor"]
        ),
    )

    save_parquet(
        volatility,
        OUTPUT / "volatility.parquet",
    )

    # ------------------------------------------------------------------
    # 5. Capital Market Assumptions
    # ------------------------------------------------------------------
    print("5/7 Building demonstration CMAs...")

    latest_momentum_z = (
        momentum_z
        .dropna(how="all")
        .iloc[-1]
    )

    expected_returns = demonstration_expected_returns(
        returns,
        latest_momentum_z,
        years=int(
            research["cma_history_years"]
        ),
        momentum_tilt=float(
            research["cma_momentum_tilt"]
        ),
        periods_per_year=int(
            research["annualization_factor"]
        ),
    )

    # Covariance must be created BEFORE the optimizer uses it.
    covariance = annualized_covariance(
        returns,
        years=int(
            research["cma_history_years"]
        ),
        periods_per_year=int(
            research["annualization_factor"]
        ),
    )

    expected_vol = expected_volatility(
        covariance
    )

    cma = pd.concat(
        [
            expected_returns,
            expected_vol,
        ],
        axis=1,
    )

    # ------------------------------------------------------------------
    # Regime-adjusted CMAs
    # ------------------------------------------------------------------
    latest_regime = (
        macro_regimes
        .dropna()
        .iloc[-1]
    )

    regime_adjusted_cma = apply_regime_tilts(
        expected_returns,
        latest_regime,
    )

    # ------------------------------------------------------------------
    # Portfolio constraints
    # ------------------------------------------------------------------
    max_weights = pd.Series(
        {
            ticker: settings["max_weight"]
            for ticker, settings
            in asset_config["assets"].items()
        },
        dtype=float,
    )

    # ------------------------------------------------------------------
    # Optimized portfolio
    # ------------------------------------------------------------------
    optimized_weights = optimize_portfolio(
        expected_returns=regime_adjusted_cma[
            "regime_adjusted_expected_return"
        ],
        covariance=covariance,
        max_weights=max_weights,
        cash_asset="BIL",
        min_cash_weight=float(
            portfolio_settings[
                "min_cash_weight"
            ]
        ),
        equity_assets=[
            "SPY",
            "VXUS",
        ],
        max_equity_weight=float(
            portfolio_settings[
                "max_equity_weight"
            ]
        ),
        risk_aversion=float(
            portfolio_settings[
                "risk_aversion"
            ]
        ),
    )

    # ------------------------------------------------------------------
    # Save CMA and optimizer outputs
    # ------------------------------------------------------------------
    save_parquet(
        cma,
        OUTPUT / "cma_expected_returns.parquet",
    )

    save_parquet(
        covariance,
        OUTPUT / "cma_covariance.parquet",
    )

    save_parquet(
        regime_adjusted_cma,
        OUTPUT / "cma_regime_adjusted.parquet",
    )

    save_parquet(
        optimized_weights.to_frame(),
        OUTPUT / "optimized_weights.parquet",
    )

    # ------------------------------------------------------------------
    # 6. Baseline portfolio
    # ------------------------------------------------------------------
    print("6/7 Building equal-weight baseline...")

    weights = equal_weight(
        assets
    ).to_frame()

    save_parquet(
        weights,
        OUTPUT / "baseline_weights.parquet",
    )

    # ------------------------------------------------------------------
    # 7. Data-quality report
    # ------------------------------------------------------------------
    print("7/7 Writing quality report...")

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "overall_passed": all(
            check.passed
            for check in checks
        ),
        "checks": checks_to_dict(
            checks
        ),
    }

    (
        OUTPUT
        / "data_quality_report.json"
    ).write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    # ------------------------------------------------------------------
    # Terminal summary
    # ------------------------------------------------------------------
    print("\nStage 1 complete.")

    print(
        f"Latest market date: "
        f"{prices.index.max().date()}"
    )

    print(
        f"Assets: {', '.join(assets)}"
    )

    print(
        f"\nLatest macro regime: "
        f"{latest_regime}"
    )

    print(
        "\nLatest demonstration CMA:"
    )

    print(
        cma
        .round(4)
        .to_string()
    )

    print(
        "\nRegime-adjusted expected returns:"
    )

    print(
        regime_adjusted_cma
        .round(4)
        .to_string()
    )

    print(
        "\nOptimized target portfolio:"
    )

    print(
        (
            optimized_weights
            * 100
        )
        .round(2)
        .astype(str)
        .add("%")
        .to_string()
    )

    print(
        "\nEqual-weight baseline:"
    )

    print(
        weights
        .round(4)
        .to_string()
    )


if __name__ == "__main__":
    main()
    
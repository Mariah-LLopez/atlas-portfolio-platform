from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from atlas.backtest.benchmarks import (
    equal_weight_benchmark,
    sixty_forty_benchmark,
)
from atlas.backtest.engine import (
    run_walk_forward_backtest,
)
from atlas.backtest.metrics import (
    annualized_return,
    annualized_volatility,
    max_drawdown,
    sharpe_ratio,
)
from atlas.config import load_yaml

DATA = Path("data/processed")


def performance_metrics(
    returns: pd.Series,
) -> dict[str, float]:
    """Calculate portfolio performance statistics."""

    return {
        "annualized_return": annualized_return(
            returns
        ),
        "annualized_volatility": (
            annualized_volatility(
                returns
            )
        ),
        "sharpe_ratio": sharpe_ratio(
            returns
        ),
        "max_drawdown": max_drawdown(
            returns
        ),
    }


def main() -> None:
    print(
        "Loading Atlas research outputs..."
    )

    returns = pd.read_parquet(
        DATA / "market_returns.parquet"
    )

    momentum_z = pd.read_parquet(
        DATA / "momentum_zscore.parquet"
    )

    macro_regime_frame = pd.read_parquet(
        DATA / "macro_regimes.parquet"
    )

    macro_regimes = (
        macro_regime_frame[
            "macro_regime"
        ]
    )

    asset_config = load_yaml(
        "configs/assets.yaml"
    )

    portfolio_config = load_yaml(
        "configs/portfolio.yaml"
    )

    portfolio_settings = (
        portfolio_config[
            "portfolio"
        ]
    )

    research = portfolio_config[
        "research"
    ]

    max_weights = pd.Series(
        {
            ticker: settings[
                "max_weight"
            ]
            for ticker, settings
            in asset_config[
                "assets"
            ].items()
        },
        dtype=float,
    )

    print(
        "Running walk-forward backtest..."
    )

    result = run_walk_forward_backtest(
        returns=returns,
        momentum_z=momentum_z,
        macro_regimes=macro_regimes,
        max_weights=max_weights,
        history_years=int(
            research[
                "cma_history_years"
            ]
        ),
        periods_per_year=int(
            research[
                "annualization_factor"
            ]
        ),
        momentum_tilt=float(
            research[
                "cma_momentum_tilt"
            ]
        ),
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
        minimum_history_days=252,
        transaction_cost_bps=float(
            portfolio_settings[
                "transaction_cost_bps"
            ]
        ),
    )

    backtest_start = (
        result
        .portfolio_returns
        .index
        .min()
    )

    backtest_end = (
        result
        .portfolio_returns
        .index
        .max()
    )

    benchmark_source = returns.loc[
        backtest_start:backtest_end
    ]

    equal_weight = (
        equal_weight_benchmark(
            benchmark_source
        )
    )

    sixty_forty = (
        sixty_forty_benchmark(
            benchmark_source
        )
    )

    comparison = pd.concat(
        [
            result.portfolio_returns.rename(
                "atlas"
            ),
            equal_weight.rename(
                "equal_weight"
            ),
            sixty_forty.rename(
                "sixty_forty"
            ),
        ],
        axis=1,
    ).dropna()

    print(
        "Calculating performance metrics..."
    )

    metrics = {
        "atlas": performance_metrics(
            comparison["atlas"]
        ),
        "equal_weight": performance_metrics(
            comparison[
                "equal_weight"
            ]
        ),
        "sixty_forty": performance_metrics(
            comparison[
                "sixty_forty"
            ]
        ),
    }

    metrics["atlas"][
        "average_monthly_turnover"
    ] = float(
        result.turnover.mean()
    )

    metrics["atlas"][
        "total_turnover"
    ] = float(
        result.turnover.sum()
    )

    metrics["metadata"] = {
        "backtest_start": str(
            comparison.index.min().date()
        ),
        "backtest_end": str(
            comparison.index.max().date()
        ),
        "rebalance_count": len(result.weights),
        "transaction_cost_bps": float(
            portfolio_settings[
                "transaction_cost_bps"
            ]
        ),
    }

    print(
        "Saving backtest outputs..."
    )

    comparison.to_parquet(
        DATA / "backtest_returns.parquet"
    )

    result.weights.to_parquet(
        DATA / "backtest_weights.parquet"
    )

    result.turnover.to_frame().to_parquet(
        DATA / "backtest_turnover.parquet"
    )

    (
        DATA
        / "backtest_metrics.json"
    ).write_text(
        json.dumps(
            metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    metrics_table = pd.DataFrame(
        {
            name: values
            for name, values
            in metrics.items()
            if name != "metadata"
        }
    ).T

    print(
        "\nBacktest complete."
    )

    print(
        f"Period: "
        f"{metrics['metadata']['backtest_start']} "
        f"to "
        f"{metrics['metadata']['backtest_end']}"
    )

    print(
        f"Rebalances: "
        f"{metrics['metadata']['rebalance_count']}"
    )

    print(
        "\nPerformance:"
    )

    print(
        metrics_table[
            [
                "annualized_return",
                "annualized_volatility",
                "sharpe_ratio",
                "max_drawdown",
            ]
        ]
        .round(4)
        .to_string()
    )

    print(
        "\nAtlas turnover:"
    )

    print(
        f"Average monthly: "
        f"{metrics['atlas']['average_monthly_turnover']:.2%}"
    )

    print(
        f"Total: "
        f"{metrics['atlas']['total_turnover']:.2f}"
    )

    print(
        "\nLatest historical Atlas weights:"
    )

    print(
        (
            result.weights.iloc[-1]
            * 100
        )
        .round(2)
        .astype(str)
        .add("%")
        .to_string()
    )


if __name__ == "__main__":
    main()
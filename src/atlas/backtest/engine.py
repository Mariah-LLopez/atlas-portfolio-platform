from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from atlas.cma.assumptions import (
    annualized_covariance,
    demonstration_expected_returns,
)
from atlas.macro.tilts import apply_regime_tilts
from atlas.portfolio.optimizer import optimize_portfolio


@dataclass
class BacktestResult:
    """Outputs produced by a walk-forward backtest."""

    portfolio_returns: pd.Series
    weights: pd.DataFrame
    turnover: pd.Series


def run_walk_forward_backtest(
    returns: pd.DataFrame,
    momentum_z: pd.DataFrame,
    macro_regimes: pd.Series,
    max_weights: pd.Series,
    *,
    history_years: int = 5,
    periods_per_year: int = 252,
    momentum_tilt: float = 0.02,
    cash_asset: str = "BIL",
    min_cash_weight: float = 0.02,
    equity_assets: list[str] | None = None,
    max_equity_weight: float | None = None,
    risk_aversion: float = 5.0,
    minimum_history_days: int = 252,
    transaction_cost_bps: float = 5.0,
    max_turnover: float | None = None,
    turnover_penalty: float = 0.0,
) -> BacktestResult:
    """Run a monthly walk-forward multi-asset backtest."""

    if returns.empty:
        raise ValueError(
            "Returns cannot be empty."
        )

    if transaction_cost_bps < 0:
        raise ValueError(
            "transaction_cost_bps "
            "cannot be negative."
        )

    returns = returns.sort_index()

    assets = returns.columns.tolist()

    max_weights = max_weights.reindex(
        assets
    )

    if max_weights.isna().any():
        missing = (
            max_weights[
                max_weights.isna()
            ]
            .index
            .tolist()
        )

        raise ValueError(
            f"Missing maximum weights "
            f"for assets: {missing}"
        )

    month_ends = (
        returns
        .resample("ME")
        .last()
        .index
    )

    available_regimes = (
        macro_regimes
        .sort_index()
        .shift(1)
    )

    weight_records: dict[
        pd.Timestamp,
        pd.Series,
    ] = {}

    previous_weights: (
        pd.Series | None
    ) = None

    for rebalance_date in month_ends:
        historical_returns = (
            returns
            .loc[:rebalance_date]
            .dropna(how="all")
        )

        if (
            len(historical_returns)
            < minimum_history_days
        ):
            continue

        available_momentum = (
            momentum_z
            .loc[:rebalance_date]
            .dropna(how="all")
        )

        if available_momentum.empty:
            continue

        latest_momentum = (
            available_momentum
            .iloc[-1]
        )

        available_macro = (
            available_regimes
            .loc[:rebalance_date]
            .dropna()
        )

        if available_macro.empty:
            continue

        latest_regime = (
            available_macro
            .iloc[-1]
        )

        expected_returns = (
            demonstration_expected_returns(
                historical_returns,
                latest_momentum,
                years=history_years,
                momentum_tilt=momentum_tilt,
                periods_per_year=periods_per_year,
            )
        )

        covariance = annualized_covariance(
            historical_returns,
            years=history_years,
            periods_per_year=periods_per_year,
        )

        adjusted_cma = apply_regime_tilts(
            expected_returns,
            latest_regime,
        )

        if previous_weights is None:
            weights = optimize_portfolio(
                expected_returns=adjusted_cma[
                    "regime_adjusted_expected_return"
                ],
                covariance=covariance,
                max_weights=max_weights,
                cash_asset=cash_asset,
                min_cash_weight=min_cash_weight,
                equity_assets=equity_assets,
                max_equity_weight=max_equity_weight,
                risk_aversion=risk_aversion,
            )

        else:
            weights = optimize_portfolio(
                expected_returns=adjusted_cma[
                    "regime_adjusted_expected_return"
                ],
                covariance=covariance,
                max_weights=max_weights,
                cash_asset=cash_asset,
                min_cash_weight=min_cash_weight,
                equity_assets=equity_assets,
                max_equity_weight=max_equity_weight,
                risk_aversion=risk_aversion,
                previous_weights=previous_weights,
                max_turnover=max_turnover,
                turnover_penalty=turnover_penalty,
            )

        weight_records[
            rebalance_date
        ] = weights

        previous_weights = weights.copy()

    if not weight_records:
        raise ValueError(
            "Backtest produced no "
            "rebalance observations."
        )

    weights_history = (
        pd.DataFrame(
            weight_records
        )
        .T
        .reindex(
            columns=assets
        )
    )

    weights_history.index.name = (
        "rebalance_date"
    )

    turnover = (
        weights_history
        .diff()
        .abs()
        .sum(axis=1)
        / 2.0
    )

    turnover.iloc[0] = 0.0
    turnover.name = "turnover"

    portfolio_returns = pd.Series(
        index=returns.index,
        dtype=float,
        name="portfolio_return",
    )

    rebalance_dates = (
        weights_history
        .index
        .tolist()
    )

    cost_rate = (
        transaction_cost_bps
        / 10_000.0
    )

    for position, rebalance_date in enumerate(
        rebalance_dates
    ):
        weights = weights_history.loc[
            rebalance_date
        ]

        if position + 1 < len(
            rebalance_dates
        ):
            next_rebalance = (
                rebalance_dates[
                    position + 1
                ]
            )

            holding_returns = returns.loc[
                (
                    returns.index
                    > rebalance_date
                )
                & (
                    returns.index
                    <= next_rebalance
                )
            ]

        else:
            holding_returns = returns.loc[
                returns.index
                > rebalance_date
            ]

        if holding_returns.empty:
            continue

        period_returns = (
            holding_returns
            .mul(
                weights,
                axis=1,
            )
            .sum(axis=1)
        )

        if position > 0:
            transaction_cost = (
                turnover.iloc[position]
                * cost_rate
            )

            period_returns.iloc[0] -= (
                transaction_cost
            )

        portfolio_returns.loc[
            period_returns.index
        ] = period_returns

    return BacktestResult(
        portfolio_returns=(
            portfolio_returns
            .dropna()
        ),
        weights=weights_history,
        turnover=turnover,
    )
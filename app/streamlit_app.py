from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA = PROJECT_ROOT / "data" / "processed"


st.set_page_config(
    page_title="Atlas Portfolio Platform",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_parquet(
    filename: str,
) -> pd.DataFrame | None:
    path = DATA / filename

    if not path.exists():
        return None

    return pd.read_parquet(path)


@st.cache_data
def load_json(
    filename: str,
) -> dict | None:
    path = DATA / filename

    if not path.exists():
        return None

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def missing_file(
    filename: str,
    command: str | None = None,
) -> None:
    st.warning(
        f"Missing required output: `{filename}`"
    )

    if command:
        st.code(
            command,
            language="powershell",
        )


def format_percent(
    value: float,
) -> str:
    return f"{value:.2%}"


def overview_page() -> None:
    st.title(
        "Atlas Multi-Asset Portfolio Platform"
    )

    st.caption(
        "Research → signals → CMAs → optimization → "
        "backtesting → attribution → monitoring"
    )

    health = load_json(
        "model_health.json"
    )

    metrics = load_json(
        "backtest_metrics.json"
    )

    weights = load_parquet(
        "optimized_weights.parquet"
    )

    if health:
        status = health.get(
            "overall_status",
            "UNKNOWN",
        )

        if status == "HEALTHY":
            st.success(
                "Model Status: HEALTHY"
            )
        elif status == "WARNING":
            st.warning(
                "Model Status: WARNING"
            )
        else:
            st.error(
                f"Model Status: {status}"
            )
    else:
        missing_file(
            "model_health.json",
            "python scripts/run_health.py",
        )

    if metrics:
        atlas = metrics.get(
            "atlas",
            {},
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "Annualized Return",
            format_percent(
                atlas.get(
                    "annualized_return",
                    0.0,
                )
            ),
        )

        col2.metric(
            "Annualized Volatility",
            format_percent(
                atlas.get(
                    "annualized_volatility",
                    0.0,
                )
            ),
        )

        col3.metric(
            "Sharpe Ratio",
            f"{atlas.get('sharpe_ratio', 0.0):.2f}",
        )

        col4.metric(
            "Max Drawdown",
            format_percent(
                atlas.get(
                    "max_drawdown",
                    0.0,
                )
            ),
        )

    st.subheader(
        "Current Target Allocation"
    )

    if weights is not None:
        current = (
            weights["weight"]
            .sort_values(
                ascending=False
            )
            * 100
        )

        st.bar_chart(
            current
        )

        display = (
            current
            .rename(
                "Target Weight (%)"
            )
            .to_frame()
            .round(2)
        )

        st.dataframe(
            display,
            use_container_width=True,
        )
    else:
        missing_file(
            "optimized_weights.parquet",
            "python scripts/run_stage1.py",
        )


def portfolio_page() -> None:
    st.title(
        "Portfolio Construction"
    )

    target = load_parquet(
        "optimized_weights.parquet"
    )

    baseline = load_parquet(
        "baseline_weights.parquet"
    )

    if target is None:
        missing_file(
            "optimized_weights.parquet",
            "python scripts/run_stage1.py",
        )
        return

    comparison = target.rename(
        columns={
            "weight": "Atlas Target"
        }
    )

    if baseline is not None:
        comparison = comparison.join(
            baseline.rename(
                columns={
                    "weight": "Equal Weight"
                }
            ),
            how="left",
        )

    comparison = (
        comparison
        * 100
    ).round(2)

    st.subheader(
        "Target vs. Baseline"
    )

    st.bar_chart(
        comparison
    )

    st.dataframe(
        comparison,
        use_container_width=True,
    )

    rebalance = load_parquet(
        "rebalance_orders.parquet"
    )

    st.subheader(
        "Rebalance Orders"
    )

    if rebalance is not None:
        st.dataframe(
            rebalance,
            use_container_width=True,
        )
    else:
        st.info(
            "Rebalance orders have not been generated yet."
        )

        st.code(
            "python scripts/generate_rebalance.py",
            language="powershell",
        )


def signals_page() -> None:
    st.title(
        "Signals & Risk"
    )

    momentum = load_parquet(
        "momentum_zscore.parquet"
    )

    volatility = load_parquet(
        "volatility.parquet"
    )

    if momentum is not None:
        st.subheader(
            "Latest Momentum Z-Scores"
        )

        latest_momentum = (
            momentum
            .dropna(how="all")
            .iloc[-1]
            .sort_values(
                ascending=False
            )
        )

        momentum_chart = (
            latest_momentum
            .rename("Momentum Z-Score")
            .rename_axis("Asset")
            .reset_index()
        )

        st.bar_chart(
            momentum_chart,
            x="Asset",
            y="Momentum Z-Score",
        )

        st.dataframe(
            momentum_chart,
            use_container_width=True,
            hide_index=True,
        )

    else:
        missing_file(
            "momentum_zscore.parquet"
        )

    if volatility is not None:
        st.subheader(
            "Latest Annualized Volatility"
        )

        latest_vol = (
            volatility
            .dropna(how="all")
            .iloc[-1]
            .sort_values(
                ascending=False
            )
        )

        volatility_chart = (
            (
                latest_vol
                * 100
            )
            .rename(
                "Annualized Volatility (%)"
            )
            .rename_axis("Asset")
            .reset_index()
        )

        st.bar_chart(
            volatility_chart,
            x="Asset",
            y="Annualized Volatility (%)",
        )

        st.dataframe(
            volatility_chart,
            use_container_width=True,
            hide_index=True,
        )

    else:
        missing_file(
            "volatility.parquet"
        )

    if volatility is not None:
        st.subheader(
            "Latest Annualized Volatility"
        )

        latest_vol = (
            volatility
            .dropna(how="all")
            .iloc[-1]
            .sort_values(
                ascending=False
            )
        )

        st.bar_chart(
            latest_vol
        )

        st.dataframe(
            (
                latest_vol
                * 100
            )
            .rename(
                "Annualized Volatility (%)"
            )
            .to_frame()
            .round(2),
            use_container_width=True,
        )


def macro_page() -> None:
    st.title(
        "Macro Regime & CMAs"
    )

    features = load_parquet(
        "macro_features.parquet"
    )

    regimes = load_parquet(
        "macro_regimes.parquet"
    )

    cma = load_parquet(
        "cma_regime_adjusted.parquet"
    )

    if regimes is not None:
        regime_series = (
            regimes[
                "macro_regime"
            ]
            .dropna()
        )

        if not regime_series.empty:
            latest_regime = (
                regime_series.iloc[-1]
            )

            st.metric(
                "Current Macro Regime",
                latest_regime
                .replace(
                    "_",
                    " "
                )
                .title(),
            )

    if features is not None:
        st.subheader(
            "Inflation & Growth"
        )

        chart_columns = [
            column
            for column in [
                "inflation_yoy",
                "growth_yoy",
            ]
            if column in features.columns
        ]

        if chart_columns:
            st.line_chart(
                features[
                    chart_columns
                ].dropna()
            )

        st.subheader(
            "Latest Macro Features"
        )

        latest_features = (
            features
            .dropna(how="all")
            .tail(1)
            .T
        )

        latest_features.columns = [
            "Latest"
        ]

        st.dataframe(
            latest_features.round(3),
            use_container_width=True,
        )

    if cma is not None:
        st.subheader(
            "Regime-Adjusted Expected Returns"
        )

        display = (
            cma.copy()
            * 100
        ).round(2)

        st.dataframe(
            display,
            use_container_width=True,
        )

        if (
            "regime_adjusted_expected_return"
            in cma.columns
        ):
            st.bar_chart(
                
                    cma[
                        "regime_adjusted_expected_return"
                    ]
                    * 100
                
            )


def backtest_page() -> None:
    st.title(
        "Walk-Forward Backtest"
    )

    returns = load_parquet(
        "backtest_returns.parquet"
    )

    metrics = load_json(
        "backtest_metrics.json"
    )

    turnover = load_parquet(
        "backtest_turnover.parquet"
    )

    if returns is None:
        missing_file(
            "backtest_returns.parquet",
            "python scripts/run_backtest.py",
        )
        return

    wealth = (
        1.0
        + returns.fillna(0.0)
    ).cumprod()

    st.subheader(
        "Growth of $1"
    )

    st.line_chart(
        wealth
    )

    if metrics:
        rows = {}

        for strategy in [
            "atlas",
            "equal_weight",
            "sixty_forty",
        ]:
            values = metrics.get(
                strategy
            )

            if not values:
                continue

            rows[strategy] = {
                "Annualized Return": (
                    values.get(
                        "annualized_return"
                    )
                ),
                "Annualized Volatility": (
                    values.get(
                        "annualized_volatility"
                    )
                ),
                "Sharpe Ratio": (
                    values.get(
                        "sharpe_ratio"
                    )
                ),
                "Max Drawdown": (
                    values.get(
                        "max_drawdown"
                    )
                ),
            }

        performance = (
            pd.DataFrame(rows)
            .T
        )

        st.subheader(
            "Performance Comparison"
        )

        st.dataframe(
            performance.style.format(
                {
                    "Annualized Return": "{:.2%}",
                    "Annualized Volatility": "{:.2%}",
                    "Sharpe Ratio": "{:.2f}",
                    "Max Drawdown": "{:.2%}",
                }
            ),
            use_container_width=True,
        )

    if turnover is not None:
        st.subheader(
            "Historical Turnover"
        )

        st.line_chart(
            turnover
        )

        maximum = float(
            turnover[
                "turnover"
            ].max()
        )

        average = float(
            turnover[
                "turnover"
            ].mean()
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Average Monthly Turnover",
            format_percent(
                average
            ),
        )

        col2.metric(
            "Maximum Monthly Turnover",
            format_percent(
                maximum
            ),
        )


def attribution_page() -> None:
    st.title(
        "Portfolio Attribution"
    )

    summary = load_parquet(
        "attribution_summary.parquet"
    )

    monthly = load_parquet(
        "attribution_monthly.parquet"
    )

    report = load_json(
        "attribution_report.json"
    )

    if report:
        reconciliation_error = float(
            report.get(
                "maximum_daily_reconciliation_error",
                0.0,
        )
    )

    st.metric(
        "Maximum Reconciliation Error",
        f"{reconciliation_error:.12f}",
    )

    if summary is not None:
        st.subheader(
            "Total Contribution by Source"
        )

        contribution = (
            summary[
                "total_contribution"
            ]
            .sort_values(
                ascending=False
            )
            * 100
        )

        st.bar_chart(
            contribution
        )

        display = (
            contribution
            .rename(
                "Total Contribution (%)"
            )
            .to_frame()
            .round(2)
        )

        st.dataframe(
            display,
            use_container_width=True,
        )
    else:
        missing_file(
            "attribution_summary.parquet",
            "python scripts/run_attribution.py",
        )

    if monthly is not None:
        st.subheader(
            "Latest 12 Months"
        )

        st.dataframe(
            (
                monthly
                .tail(12)
                * 100
            ).round(2),
            use_container_width=True,
        )


def health_page() -> None:
    st.title(
        "System Health"
    )

    health = load_json(
        "model_health.json"
    )

    if health is None:
        missing_file(
            "model_health.json",
            "python scripts/run_health.py",
        )
        return

    status = health.get(
        "overall_status",
        "UNKNOWN",
    )

    if status == "HEALTHY":
        st.success(
            "ATLAS MODEL STATUS: HEALTHY"
        )
    elif status == "WARNING":
        st.warning(
            "ATLAS MODEL STATUS: WARNING"
        )
    else:
        st.error(
            f"ATLAS MODEL STATUS: {status}"
        )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Passed",
        health.get(
            "passed_checks",
            0,
        ),
    )

    col2.metric(
        "Failed",
        health.get(
            "failed_checks",
            0,
        ),
    )

    col3.metric(
        "Warnings",
        health.get(
            "warning_checks",
            0,
        ),
    )

    checks = pd.DataFrame(
        health.get(
            "checks",
            []
        )
    )

    if not checks.empty:
        st.subheader(
            "Model Controls"
        )

        st.dataframe(
            checks,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        f"Report generated: "
        f"{health.get('generated_at_utc', 'Unknown')}"
    )


pages = [
    st.Page(
        overview_page,
        title="Overview",
        icon="🏠",
        default=True,
    ),
    st.Page(
        portfolio_page,
        title="Portfolio",
        icon="⚖️",
    ),
    st.Page(
        signals_page,
        title="Signals",
        icon="📡",
    ),
    st.Page(
        macro_page,
        title="Macro & CMAs",
        icon="🌎",
    ),
    st.Page(
        backtest_page,
        title="Backtest",
        icon="📈",
    ),
    st.Page(
        attribution_page,
        title="Attribution",
        icon="🧩",
    ),
    st.Page(
        health_page,
        title="System Health",
        icon="❤️",
    ),
]


navigation = st.navigation(
    pages
)

navigation.run()
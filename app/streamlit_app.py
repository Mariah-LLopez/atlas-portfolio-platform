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
    """Load a processed Parquet artifact if it exists."""

    path = DATA / filename

    if not path.exists():
        return None

    return pd.read_parquet(path)


@st.cache_data
def load_json(
    filename: str,
) -> dict | None:
    """Load a processed JSON artifact if it exists."""

    path = DATA / filename

    if not path.exists():
        return None

    return json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )


def missing_file(
    filename: str,
    command: str | None = None,
) -> None:
    """Display a friendly missing-output message."""

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
    """Format a decimal as a percentage."""

    return f"{value:.2%}"


def build_bar_frame(
    series: pd.Series,
    *,
    multiplier: float = 1.0,
) -> pd.DataFrame:
    """Convert a Series into chart-safe asset/value columns."""

    frame = (
        series.astype(float)
        .mul(multiplier)
        .rename("value")
        .rename_axis("asset")
        .reset_index()
    )

    frame["asset"] = frame["asset"].astype(str)

    return frame


# ======================================================================
# OVERVIEW
# ======================================================================


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

    # ------------------------------------------------------------------
    # Model health
    # ------------------------------------------------------------------
    if health:
        status = str(
            health.get(
                "overall_status",
                "UNKNOWN",
            )
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

    # ------------------------------------------------------------------
    # Performance metrics
    # ------------------------------------------------------------------
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
                float(
                    atlas.get(
                        "annualized_return",
                        0.0,
                    )
                )
            ),
        )

        col2.metric(
            "Annualized Volatility",
            format_percent(
                float(
                    atlas.get(
                        "annualized_volatility",
                        0.0,
                    )
                )
            ),
        )

        col3.metric(
            "Sharpe Ratio",
            (
                f"{float(
                    atlas.get(
                        'sharpe_ratio',
                        0.0,
                    )
                ):.2f}"
            ),
        )

        col4.metric(
            "Max Drawdown",
            format_percent(
                float(
                    atlas.get(
                        "max_drawdown",
                        0.0,
                    )
                )
            ),
        )

    else:
        missing_file(
            "backtest_metrics.json",
            "python scripts/run_backtest.py",
        )

    # ------------------------------------------------------------------
    # Target allocation
    # ------------------------------------------------------------------
    st.subheader(
        "Current Target Allocation"
    )

    if weights is not None:
        current = (
            weights["weight"]
            .astype(float)
            .sort_values(
                ascending=False
            )
        )

        chart = build_bar_frame(
            current,
            multiplier=100.0,
        )

        st.bar_chart(
            chart,
            x="asset",
            y="value",
        )

        display = (
            current
            .mul(100.0)
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


# ======================================================================
# PORTFOLIO
# ======================================================================


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
            "weight": "Atlas Target",
        }
    )

    if baseline is not None:
        comparison = comparison.join(
            baseline.rename(
                columns={
                    "weight": "Equal Weight",
                }
            ),
            how="left",
        )

    comparison = (
        comparison.astype(float)
        .mul(100.0)
        .round(2)
    )

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

    # ------------------------------------------------------------------
    # Rebalance orders
    # ------------------------------------------------------------------
    st.subheader(
        "Rebalance Orders"
    )

    rebalance = load_parquet(
        "rebalance_orders.parquet"
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


# ======================================================================
# SIGNALS
# ======================================================================


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

    # ------------------------------------------------------------------
    # Momentum
    # ------------------------------------------------------------------
    if momentum is not None:
        st.subheader(
            "Latest Momentum Z-Scores"
        )

        momentum_clean = (
            momentum
            .dropna(how="all")
        )

        if not momentum_clean.empty:
            latest_momentum = (
                momentum_clean
                .iloc[-1]
                .dropna()
                .astype(float)
                .sort_values(
                    ascending=False
                )
            )

            momentum_chart = (
                build_bar_frame(
                    latest_momentum
                )
            )

            st.bar_chart(
                momentum_chart,
                x="asset",
                y="value",
            )

            momentum_display = (
                latest_momentum
                .rename(
                    "Momentum Z-Score"
                )
                .to_frame()
                .round(3)
            )

            st.dataframe(
                momentum_display,
                use_container_width=True,
            )

        else:
            st.info(
                "Momentum data contains no usable observations."
            )

    else:
        missing_file(
            "momentum_zscore.parquet",
            "python scripts/run_stage1.py",
        )

    # ------------------------------------------------------------------
    # Volatility
    # ------------------------------------------------------------------
    if volatility is not None:
        st.subheader(
            "Latest Annualized Volatility"
        )

        volatility_clean = (
            volatility
            .dropna(how="all")
        )

        if not volatility_clean.empty:
            latest_vol = (
                volatility_clean
                .iloc[-1]
                .dropna()
                .astype(float)
                .sort_values(
                    ascending=False
                )
            )

            volatility_chart = (
                build_bar_frame(
                    latest_vol,
                    multiplier=100.0,
                )
            )

            st.bar_chart(
                volatility_chart,
                x="asset",
                y="value",
            )

            volatility_display = (
                latest_vol
                .mul(100.0)
                .rename(
                    "Annualized Volatility (%)"
                )
                .to_frame()
                .round(2)
            )

            st.dataframe(
                volatility_display,
                use_container_width=True,
            )

        else:
            st.info(
                "Volatility data contains no usable observations."
            )

    else:
        missing_file(
            "volatility.parquet",
            "python scripts/run_stage1.py",
        )


# ======================================================================
# MACRO + CMAs
# ======================================================================


def macro_page() -> None:
    st.title(
        "Macro Regime & Capital Market Assumptions"
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

    # ------------------------------------------------------------------
    # Current regime
    # ------------------------------------------------------------------
    if regimes is not None:
        if "macro_regime" in regimes.columns:
            regime_series = (
                regimes[
                    "macro_regime"
                ]
                .dropna()
            )

            if not regime_series.empty:
                latest_regime = str(
                    regime_series.iloc[-1]
                )

                st.metric(
                    "Current Macro Regime",
                    (
                        latest_regime
                        .replace(
                            "_",
                            " ",
                        )
                        .title()
                    ),
                )

    else:
        missing_file(
            "macro_regimes.parquet",
            "python scripts/run_stage1.py",
        )

    # ------------------------------------------------------------------
    # Macro features
    # ------------------------------------------------------------------
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
            macro_chart = (
                features[
                    chart_columns
                ]
                .dropna(
                    how="all"
                )
            )

            st.line_chart(
                macro_chart
            )

        st.subheader(
            "Latest Macro Features"
        )

        features_clean = (
            features
            .dropna(how="all")
        )

        if not features_clean.empty:
            latest_features = (
                features_clean
                .tail(1)
                .T
            )

            latest_features.columns = [
                "Latest",
            ]

            st.dataframe(
                latest_features.round(3),
                use_container_width=True,
            )

    else:
        missing_file(
            "macro_features.parquet",
            "python scripts/run_stage1.py",
        )

    # ------------------------------------------------------------------
    # CMAs
    # ------------------------------------------------------------------
    if cma is not None:
        st.subheader(
            "Regime-Adjusted Expected Returns"
        )

        cma_display = (
            cma.astype(float)
            .mul(100.0)
            .round(2)
        )

        st.dataframe(
            cma_display,
            use_container_width=True,
        )

        if (
            "regime_adjusted_expected_return"
            in cma.columns
        ):
            cma_series = (
                cma[
                    "regime_adjusted_expected_return"
                ]
                .astype(float)
                .sort_values(
                    ascending=False
                )
            )

            cma_chart = build_bar_frame(
                cma_series,
                multiplier=100.0,
            )

            st.bar_chart(
                cma_chart,
                x="asset",
                y="value",
            )

    else:
        missing_file(
            "cma_regime_adjusted.parquet",
            "python scripts/run_stage1.py",
        )


# ======================================================================
# BACKTEST
# ======================================================================


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

    # ------------------------------------------------------------------
    # Wealth curves
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Performance metrics
    # ------------------------------------------------------------------
    if metrics:
        rows: dict[
            str,
            dict[str, float],
        ] = {}

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

            rows[
                strategy
            ] = {
                "Annualized Return": float(
                    values.get(
                        "annualized_return",
                        0.0,
                    )
                ),
                "Annualized Volatility": float(
                    values.get(
                        "annualized_volatility",
                        0.0,
                    )
                ),
                "Sharpe Ratio": float(
                    values.get(
                        "sharpe_ratio",
                        0.0,
                    )
                ),
                "Max Drawdown": float(
                    values.get(
                        "max_drawdown",
                        0.0,
                    )
                ),
            }

        performance = (
            pd.DataFrame(
                rows
            )
            .T
        )

        if not performance.empty:
            st.subheader(
                "Performance Comparison"
            )

            performance_display = (
                performance.copy()
            )

            performance_display[
                "Annualized Return"
            ] = performance_display[
                "Annualized Return"
            ].map(
                lambda value: (
                    f"{value:.2%}"
                )
            )

            performance_display[
                "Annualized Volatility"
            ] = performance_display[
                "Annualized Volatility"
            ].map(
                lambda value: (
                    f"{value:.2%}"
                )
            )

            performance_display[
                "Sharpe Ratio"
            ] = performance_display[
                "Sharpe Ratio"
            ].map(
                lambda value: (
                    f"{value:.2f}"
                )
            )

            performance_display[
                "Max Drawdown"
            ] = performance_display[
                "Max Drawdown"
            ].map(
                lambda value: (
                    f"{value:.2%}"
                )
            )

            st.dataframe(
                performance_display,
                use_container_width=True,
            )

    # ------------------------------------------------------------------
    # Turnover
    # ------------------------------------------------------------------
    if turnover is not None:
        if "turnover" in turnover.columns:
            st.subheader(
                "Historical Turnover"
            )

            turnover_chart = (
                turnover[
                    [
                        "turnover",
                    ]
                ]
                .astype(float)
                .mul(100.0)
            )

            turnover_chart = (
                turnover_chart.rename(
                    columns={
                        "turnover": (
                            "Turnover (%)"
                        ),
                    }
                )
            )

            st.line_chart(
                turnover_chart
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

            col1, col2 = st.columns(
                2
            )

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


# ======================================================================
# ATTRIBUTION
# ======================================================================


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

    # ------------------------------------------------------------------
    # Reconciliation
    # ------------------------------------------------------------------
    if report:
        reconciliation_value = float(
            report.get(
                "maximum_daily_reconciliation_error",
                0.0,
            )
        )

        st.metric(
            "Maximum Reconciliation Error",
            f"{reconciliation_value:.12f}",
        )

    # ------------------------------------------------------------------
    # Total contribution
    # ------------------------------------------------------------------
    if summary is not None:
        if (
            "total_contribution"
            in summary.columns
        ):
            st.subheader(
                "Total Contribution by Source"
            )

            contribution = (
                summary[
                    "total_contribution"
                ]
                .astype(float)
                .sort_values(
                    ascending=False
                )
            )

            contribution_chart = (
                build_bar_frame(
                    contribution,
                    multiplier=100.0,
                )
            )

            st.bar_chart(
                contribution_chart,
                x="asset",
                y="value",
            )

            display = (
                contribution
                .mul(100.0)
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

    # ------------------------------------------------------------------
    # Monthly attribution
    # ------------------------------------------------------------------
    if monthly is not None:
        st.subheader(
            "Latest 12 Months"
        )

        monthly_display = (
            monthly
            .tail(12)
            .astype(float)
            .mul(100.0)
            .round(2)
        )

        st.dataframe(
            monthly_display,
            use_container_width=True,
        )


# ======================================================================
# SYSTEM HEALTH
# ======================================================================


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

    status = str(
        health.get(
            "overall_status",
            "UNKNOWN",
        )
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

    col1, col2, col3 = st.columns(
        3
    )

    col1.metric(
        "Passed",
        int(
            health.get(
                "passed_checks",
                0,
            )
        ),
    )

    col2.metric(
        "Failed",
        int(
            health.get(
                "failed_checks",
                0,
            )
        ),
    )

    col3.metric(
        "Warnings",
        int(
            health.get(
                "warning_checks",
                0,
            )
        ),
    )

    checks = pd.DataFrame(
        health.get(
            "checks",
            [],
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

    generated_at = str(
        health.get(
            "generated_at_utc",
            "Unknown",
        )
    )

    st.caption(
        f"Report generated: {generated_at}"
    )


# ======================================================================
# NAVIGATION
# ======================================================================


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
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from atlas.config import load_yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA = PROJECT_ROOT / "data" / "processed"
DOCS = PROJECT_ROOT / "docs"

st.set_page_config(
    page_title="Atlas | Multi-Asset Research Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.block-container {padding-top:1.6rem; padding-bottom:3rem; max-width:1500px;}
[data-testid="stSidebar"] {border-right:1px solid rgba(148,163,184,.18);}
.atlas-brand {padding:.2rem 0 1.1rem 0;}
.atlas-brand-name {font-size:1.45rem;font-weight:800;letter-spacing:.10em;line-height:1;}
.atlas-brand-subtitle {font-size:.76rem;opacity:.72;margin-top:.45rem;letter-spacing:.03em;}
.atlas-eyebrow {color:#2563EB;font-size:.74rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;margin-bottom:.45rem;}
.atlas-title {font-size:2.15rem;font-weight:800;letter-spacing:-.035em;line-height:1.1;margin-bottom:.35rem;}
.atlas-subtitle {color:#64748B;font-size:.98rem;max-width:920px;margin-bottom:1.2rem;}
.atlas-section-title {font-size:1.12rem;font-weight:750;margin-top:.25rem;margin-bottom:.2rem;}
.atlas-section-note {color:#64748B;font-size:.84rem;margin-bottom:.7rem;}
.atlas-status {border-radius:999px;display:inline-block;font-size:.75rem;font-weight:800;letter-spacing:.04em;padding:.30rem .70rem;margin-bottom:.75rem;}
.atlas-status-healthy {background:#DCFCE7;color:#166534;border:1px solid #BBF7D0;}
.atlas-status-warning {background:#FEF3C7;color:#92400E;border:1px solid #FDE68A;}
.atlas-status-failed {background:#FEE2E2;color:#991B1B;border:1px solid #FECACA;}
.atlas-callout {border-left:4px solid #2563EB;background:rgba(37,99,235,.06);border-radius:.55rem;padding:.9rem 1rem;margin:.7rem 0 .9rem 0;color:#334155;font-size:.90rem;}
.atlas-flow {font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;background:#0F172A;color:#E2E8F0;border-radius:.75rem;padding:1rem 1.1rem;line-height:1.75;overflow-x:auto;}
div[data-testid="stMetric"] {background:rgba(255,255,255,.72);}
div[data-testid="stDataFrame"] {border-radius:.7rem;overflow:hidden;}
hr {border-color:rgba(148,163,184,.18);}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_parquet(filename: str) -> pd.DataFrame | None:
    path = DATA / filename
    if not path.exists():
        return None
    return pd.read_parquet(path)


@st.cache_data
def load_json(filename: str) -> dict | None:
    path = DATA / filename
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data
def load_text(filename: str) -> str | None:
    path = DOCS / filename
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


@st.cache_data
def load_portfolio_config() -> dict:
    return load_yaml(str(PROJECT_ROOT / "configs" / "portfolio.yaml"))


def pct(value: float) -> str:
    return f"{value:.2%}"


def page_header(title: str, subtitle: str, eyebrow: str) -> None:
    st.markdown(
        (
            f'<div class="atlas-eyebrow">{eyebrow}</div>'
            f'<div class="atlas-title">{title}</div>'
            f'<div class="atlas-subtitle">{subtitle}</div>'
        ),
        unsafe_allow_html=True,
    )


def section_header(title: str, note: str | None = None) -> None:
    st.markdown(
        f'<div class="atlas-section-title">{title}</div>',
        unsafe_allow_html=True,
    )
    if note:
        st.markdown(
            f'<div class="atlas-section-note">{note}</div>',
            unsafe_allow_html=True,
        )


def missing_file(filename: str, command: str | None = None) -> None:
    st.info(f"`{filename}` has not been generated yet.")
    if command:
        st.code(command, language="powershell")


def status_chip(status: str) -> None:
    normalized = status.upper()
    if normalized == "HEALTHY":
        css_class = "atlas-status-healthy"
    elif normalized == "WARNING":
        css_class = "atlas-status-warning"
    else:
        css_class = "atlas-status-failed"
    st.markdown(
        (
            f'<span class="atlas-status {css_class}">'
            f"MODEL STATUS · {normalized}</span>"
        ),
        unsafe_allow_html=True,
    )


def single_series_bar(series: pd.Series, multiplier: float = 1.0) -> None:
    chart = (
        series.astype(float)
        .mul(multiplier)
        .rename("Value")
        .rename_axis("Asset")
        .reset_index()
    )
    chart["Asset"] = chart["Asset"].astype(str)
    st.bar_chart(chart, x="Asset", y="Value")


def timeseries_chart(frame: pd.DataFrame) -> None:
    if frame.empty:
        return
    safe = frame.copy()
    safe.index.name = "Date"
    safe = safe.reset_index()
    safe.columns = [str(column) for column in safe.columns]
    values = [column for column in safe.columns if column != "Date"]
    if values:
        st.line_chart(safe, x="Date", y=values)


def latest_regime() -> str | None:
    regimes = load_parquet("macro_regimes.parquet")
    if regimes is None or "macro_regime" not in regimes.columns:
        return None
    clean = regimes["macro_regime"].dropna()
    if clean.empty:
        return None
    return str(clean.iloc[-1])


def regime_label(value: str | None) -> str:
    if not value:
        return "Unavailable"
    return value.replace("_", " ").title()


def sidebar_brand() -> None:
    st.sidebar.markdown(
        """
<div class="atlas-brand">
    <div class="atlas-brand-name">ATLAS</div>
    <div class="atlas-brand-subtitle">Multi-Asset Research Platform</div>
</div>
""",
        unsafe_allow_html=True,
    )
    health = load_json("model_health.json")
    status = str(health.get("overall_status", "UNKNOWN")) if health else "UNKNOWN"
    st.sidebar.caption(f"Model status · {status}")


def overview_page() -> None:
    page_header(
        "Executive Overview",
        "Latest allocation, model state, risk-adjusted performance, and portfolio operations in one PM-facing view.",
        "Portfolio Intelligence",
    )

    health = load_json("model_health.json")
    metrics = load_json("backtest_metrics.json")
    weights = load_parquet("optimized_weights.parquet")
    attribution = load_parquet("attribution_summary.parquet")
    rebalance = load_parquet("rebalance_orders.parquet")
    turnover = load_parquet("backtest_turnover.parquet")

    status = str(health.get("overall_status", "UNKNOWN")) if health else "UNKNOWN"
    status_chip(status)

    atlas = metrics.get("atlas", {}) if metrics else {}
    regime = latest_regime()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Annualized Return", pct(float(atlas.get("annualized_return", 0.0))), border=True)
    c2.metric("Sharpe Ratio", f"{float(atlas.get('sharpe_ratio', 0.0)):.2f}", border=True)
    c3.metric("Volatility", pct(float(atlas.get("annualized_volatility", 0.0))), border=True)
    c4.metric("Max Drawdown", pct(float(atlas.get("max_drawdown", 0.0))), border=True)
    c5.metric("Macro Regime", regime_label(regime), border=True)

    passed = int(health.get("passed_checks", 0)) if health else 0
    total = int(health.get("check_count", 0)) if health else 0
    c6.metric("Health Checks", f"{passed}/{total}" if total else "—", border=True)

    st.divider()
    left, right = st.columns([1.15, 1])

    with left:
        with st.container(border=True):
            section_header("Current Target Allocation", "Latest constrained multi-asset target.")
            if weights is not None and "weight" in weights.columns:
                target = weights["weight"].astype(float).sort_values(ascending=False)
                single_series_bar(target, 100.0)
                st.dataframe(
                    target.mul(100.0).rename("Target Weight (%)").to_frame().round(2),
                    use_container_width=True,
                )
            else:
                missing_file("optimized_weights.parquet", "python scripts/run_stage1.py")

    with right:
        with st.container(border=True):
            section_header("Performance vs Benchmarks", "Walk-forward results over the common test window.")
            rows: dict[str, dict[str, str]] = {}
            if metrics:
                mapping = {"atlas": "Atlas", "equal_weight": "Equal Weight", "sixty_forty": "60/40"}
                for key, label in mapping.items():
                    values = metrics.get(key)
                    if not values:
                        continue
                    rows[label] = {
                        "Return": pct(float(values.get("annualized_return", 0.0))),
                        "Volatility": pct(float(values.get("annualized_volatility", 0.0))),
                        "Sharpe": f"{float(values.get('sharpe_ratio', 0.0)):.2f}",
                        "Max Drawdown": pct(float(values.get("max_drawdown", 0.0))),
                    }
            if rows:
                st.dataframe(pd.DataFrame(rows).T, use_container_width=True)
            else:
                missing_file("backtest_metrics.json", "python scripts/run_backtest.py")

    st.divider()
    b1, b2, b3 = st.columns(3)

    with b1:
        with st.container(border=True):
            section_header("Top Attribution Driver", "Largest full-period contribution source.")
            if attribution is not None and "total_contribution" in attribution.columns and not attribution.empty:
                contrib = attribution["total_contribution"].astype(float)
                st.metric(str(contrib.idxmax()), pct(float(contrib.max())))
                st.caption(f"Largest detractor: {contrib.idxmin()} ({pct(float(contrib.min()))})")
            else:
                st.caption("Run attribution to populate this panel.")

    with b2:
        with st.container(border=True):
            section_header("Portfolio Turnover", "Trading intensity after turnover controls.")
            if turnover is not None and "turnover" in turnover.columns:
                series = turnover["turnover"].astype(float)
                st.metric("Average Monthly", pct(float(series.mean())))
                st.caption(f"Maximum observed: {pct(float(series.max()))}")
            else:
                st.caption("Run the backtest to populate this panel.")

    with b3:
        with st.container(border=True):
            section_header("Latest Rebalance", "Operational order summary.")
            if rebalance is not None and "action" in rebalance.columns:
                actions = rebalance["action"].astype(str)
                buys = int((actions == "BUY").sum())
                sells = int((actions == "SELL").sum())
                holds = int((actions == "HOLD").sum())
                st.metric("Executable Actions", str(buys + sells))
                st.caption(f"{buys} BUY · {sells} SELL · {holds} HOLD")
            else:
                st.caption("Generate rebalance orders to populate this panel.")

    if weights is not None and "weight" in weights.columns:
        target = weights["weight"].astype(float)
        equity = float(target.reindex(["SPY", "VXUS"]).fillna(0.0).sum())
        cash = float(target.get("BIL", 0.0))
        largest_asset = str(target.idxmax())
        largest_weight = float(target.max())
        st.markdown(
            (
                '<div class="atlas-callout"><b>Current portfolio read:</b> '
                f"{regime_label(regime)} regime; {pct(equity)} equity exposure; "
                f"{pct(cash)} cash; largest allocation is {largest_asset} at {pct(largest_weight)}."
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def research_page() -> None:
    page_header(
        "Research & Market Signals",
        "Transparent signal engineering, macro classification, risk measures, and regime-conditioned CMAs.",
        "Quant Research",
    )

    momentum = load_parquet("momentum_zscore.parquet")
    volatility = load_parquet("volatility.parquet")
    features = load_parquet("macro_features.parquet")
    regimes = load_parquet("macro_regimes.parquet")
    cma = load_parquet("cma_regime_adjusted.parquet")

    tab1, tab2, tab3 = st.tabs(["Signals & Risk", "Macro Regime", "Capital Market Assumptions"])

    with tab1:
        left, right = st.columns(2)
        with left:
            with st.container(border=True):
                section_header("Latest Momentum Z-Scores", "Cross-sectional 12-1 momentum ranking.")
                if momentum is not None and not momentum.dropna(how="all").empty:
                    latest = momentum.dropna(how="all").iloc[-1].dropna().astype(float).sort_values(ascending=False)
                    single_series_bar(latest)
                    st.dataframe(latest.rename("Momentum Z-Score").to_frame().round(3), use_container_width=True)
                else:
                    missing_file("momentum_zscore.parquet")

        with right:
            with st.container(border=True):
                section_header("Latest Annualized Volatility", "Rolling realized risk estimate.")
                if volatility is not None and not volatility.dropna(how="all").empty:
                    latest = volatility.dropna(how="all").iloc[-1].dropna().astype(float).sort_values(ascending=False)
                    single_series_bar(latest, 100.0)
                    st.dataframe(latest.mul(100.0).rename("Annualized Volatility (%)").to_frame().round(2), use_container_width=True)
                else:
                    missing_file("volatility.parquet")

    with tab2:
        regime = latest_regime()
        k1, k2, k3 = st.columns(3)
        k1.metric("Current Regime", regime_label(regime), border=True)

        if features is not None and not features.dropna(how="all").empty:
            latest = features.dropna(how="all").iloc[-1]
            k2.metric("Inflation YoY", f"{float(latest.get('inflation_yoy', 0.0)):.2f}%", border=True)
            k3.metric("Industrial Production YoY", f"{float(latest.get('growth_yoy', 0.0)):.2f}%", border=True)

            with st.container(border=True):
                section_header("Growth and Inflation History", "Macro features used by the regime classifier.")
                cols = [c for c in ["inflation_yoy", "growth_yoy"] if c in features.columns]
                if cols:
                    timeseries_chart(features[cols].dropna(how="all"))

            with st.expander("Latest macro feature vector"):
                st.dataframe(latest.rename("Latest").to_frame().round(3), use_container_width=True)

        if regimes is not None and "macro_regime" in regimes.columns:
            with st.expander("Recent regime history"):
                st.dataframe(regimes[["macro_regime"]].dropna().tail(18), use_container_width=True)

    with tab3:
        with st.container(border=True):
            section_header("Regime-Adjusted Expected Returns", "Baseline CMAs plus transparent macro regime tilts.")
            if cma is not None:
                st.dataframe(cma.astype(float).mul(100.0).round(2), use_container_width=True)
                column = "regime_adjusted_expected_return"
                if column in cma.columns:
                    single_series_bar(cma[column].astype(float).sort_values(ascending=False), 100.0)
            else:
                missing_file("cma_regime_adjusted.parquet", "python scripts/run_stage1.py")

        st.markdown(
            """
<div class="atlas-callout"><b>Research discipline:</b> regime tilts are demonstration priors, not guaranteed forecasts. Their usefulness is evaluated through walk-forward testing rather than tuned to make historical performance look better.</div>
""",
            unsafe_allow_html=True,
        )


def portfolio_page() -> None:
    page_header(
        "Portfolio Construction & Rebalancing",
        "PM-defined constraints, optimized target weights, current holdings, and executable BUY / SELL / HOLD instructions.",
        "Portfolio Operations",
    )

    target = load_parquet("optimized_weights.parquet")
    baseline = load_parquet("baseline_weights.parquet")
    rebalance = load_parquet("rebalance_orders.parquet")
    config = load_portfolio_config()
    settings = config.get("portfolio", {})

    if target is None or "weight" not in target.columns:
        missing_file("optimized_weights.parquet", "python scripts/run_stage1.py")
        return

    weights = target["weight"].astype(float)
    equity = float(weights.reindex(["SPY", "VXUS"]).fillna(0.0).sum())
    cash = float(weights.get("BIL", 0.0))
    max_equity = float(settings.get("max_equity_weight", 0.60))
    min_cash = float(settings.get("min_cash_weight", 0.02))
    turnover_limit = float(settings.get("max_turnover_per_rebalance", 0.20))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Equity Exposure", pct(equity), f"{pct(max_equity)} cap", delta_color="off", border=True)
    c2.metric("Cash Allocation", pct(cash), f"{pct(min_cash)} floor", delta_color="off", border=True)
    c3.metric("Largest Position", f"{weights.idxmax()} · {pct(float(weights.max()))}", border=True)
    c4.metric("Turnover Policy", pct(turnover_limit), border=True)

    st.divider()
    left, right = st.columns([1.1, 1])

    with left:
        with st.container(border=True):
            section_header("Target vs Equal-Weight Baseline", "Optimized portfolio compared with a neutral baseline.")
            comparison = target.rename(columns={"weight": "Atlas Target"})
            if baseline is not None and "weight" in baseline.columns:
                comparison = comparison.join(baseline.rename(columns={"weight": "Equal Weight"}), how="left")
            comparison = comparison.astype(float).mul(100.0)
            chart = comparison.copy()
            chart.index.name = "Asset"
            chart = chart.reset_index()
            ycols = [c for c in chart.columns if c != "Asset"]
            st.bar_chart(chart, x="Asset", y=ycols)
            st.dataframe(comparison.round(2), use_container_width=True)

    with right:
        with st.container(border=True):
            section_header("Constraint Utilization", "Key policy rules and current utilization.")
            table = pd.DataFrame(
                [
                    {"Constraint": "Maximum equity", "Current": equity, "Limit": max_equity, "Status": "PASS" if equity <= max_equity + 1e-6 else "FAIL"},
                    {"Constraint": "Minimum cash", "Current": cash, "Limit": min_cash, "Status": "PASS" if cash + 1e-6 >= min_cash else "FAIL"},
                    {"Constraint": "Fully invested", "Current": float(weights.sum()), "Limit": 1.0, "Status": "PASS" if abs(float(weights.sum()) - 1.0) <= 1e-6 else "FAIL"},
                ]
            )
            display = table.copy()
            display["Current"] = display["Current"].map(pct)
            display["Limit"] = display["Limit"].map(pct)
            st.dataframe(display, use_container_width=True, hide_index=True)
            st.caption("Individual asset caps are also enforced from configs/assets.yaml.")

    st.divider()
    section_header("Rebalance Orders", "Current holdings translated into the latest optimized target.")

    if rebalance is None:
        missing_file("rebalance_orders.parquet", "python scripts/generate_rebalance.py")
        return

    display = rebalance.copy()
    preferred = ["action", "current_value", "current_weight", "target_weight", "target_value", "trade_value", "executable_trade_value", "latest_price", "estimated_shares"]
    visible = [column for column in preferred if column in display.columns]
    display = display[visible]
    for column in ["current_weight", "target_weight"]:
        if column in display.columns:
            display[column] = display[column].astype(float).mul(100.0)
    st.dataframe(display, use_container_width=True)

    if "action" in rebalance.columns:
        counts = rebalance["action"].astype(str).value_counts()
        a1, a2, a3 = st.columns(3)
        a1.metric("BUY orders", str(int(counts.get("BUY", 0))), border=True)
        a2.metric("SELL orders", str(int(counts.get("SELL", 0))), border=True)
        a3.metric("HOLD positions", str(int(counts.get("HOLD", 0))), border=True)


def backtest_page() -> None:
    page_header(
        "Walk-Forward Backtest",
        "Monthly portfolio formation using only information available at each rebalance, including transaction costs and turnover controls.",
        "Model Validation",
    )

    returns = load_parquet("backtest_returns.parquet")
    metrics = load_json("backtest_metrics.json")
    turnover = load_parquet("backtest_turnover.parquet")
    historical_weights = load_parquet("backtest_weights.parquet")

    if returns is None:
        missing_file("backtest_returns.parquet", "python scripts/run_backtest.py")
        return

    atlas = metrics.get("atlas", {}) if metrics else {}
    equal_weight = metrics.get("equal_weight", {}) if metrics else {}
    sixty_forty = metrics.get("sixty_forty", {}) if metrics else {}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Atlas Return", pct(float(atlas.get("annualized_return", 0.0))), border=True)
    c2.metric("Atlas Sharpe", f"{float(atlas.get('sharpe_ratio', 0.0)):.2f}", border=True)
    c3.metric("Atlas Drawdown", pct(float(atlas.get("max_drawdown", 0.0))), border=True)
    best_benchmark = max(float(equal_weight.get("sharpe_ratio", 0.0)), float(sixty_forty.get("sharpe_ratio", 0.0)))
    c4.metric("Sharpe vs Best Benchmark", f"{float(atlas.get('sharpe_ratio', 0.0)) - best_benchmark:+.2f}", border=True)

    with st.container(border=True):
        section_header("Growth of $1", "Atlas compared with equal-weight and a 60/40 proxy.")
        timeseries_chart((1.0 + returns.fillna(0.0)).cumprod())

    left, right = st.columns([1.15, 1])
    with left:
        with st.container(border=True):
            section_header("Performance Comparison", "Risk and return statistics over the shared test window.")
            rows: dict[str, dict[str, str]] = {}
            if metrics:
                mapping = {"atlas": "Atlas", "equal_weight": "Equal Weight", "sixty_forty": "60/40"}
                for key, label in mapping.items():
                    values = metrics.get(key)
                    if values:
                        rows[label] = {
                            "Ann. Return": pct(float(values.get("annualized_return", 0.0))),
                            "Ann. Volatility": pct(float(values.get("annualized_volatility", 0.0))),
                            "Sharpe": f"{float(values.get('sharpe_ratio', 0.0)):.2f}",
                            "Max Drawdown": pct(float(values.get("max_drawdown", 0.0))),
                        }
            st.dataframe(pd.DataFrame(rows).T, use_container_width=True)

    with right:
        with st.container(border=True):
            section_header("Turnover", "Historical trading intensity after the hard turnover control.")
            if turnover is not None and "turnover" in turnover.columns:
                series = turnover["turnover"].astype(float)
                timeseries_chart(series.mul(100.0).rename("Turnover (%)").to_frame())
                t1, t2 = st.columns(2)
                t1.metric("Average", pct(float(series.mean())))
                t2.metric("Maximum", pct(float(series.max())))

    if historical_weights is not None:
        with st.expander("Recent historical target weights"):
            st.dataframe(historical_weights.tail(12).astype(float).mul(100.0).round(2), use_container_width=True)


def attribution_page() -> None:
    page_header(
        "Portfolio Attribution",
        "Explain historical portfolio returns by asset contribution and explicit transaction-cost drag.",
        "Performance Intelligence",
    )

    summary = load_parquet("attribution_summary.parquet")
    monthly = load_parquet("attribution_monthly.parquet")
    report = load_json("attribution_report.json")
    reconciliation = float(report.get("maximum_daily_reconciliation_error", 0.0)) if report else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("Max Reconciliation Error", f"{reconciliation:.12f}", border=True)

    if summary is not None and "total_contribution" in summary.columns:
        contrib = summary["total_contribution"].astype(float)
        c2.metric("Largest Contributor", str(contrib.idxmax()), pct(float(contrib.max())), delta_color="off", border=True)
        c3.metric("Largest Detractor", str(contrib.idxmin()), pct(float(contrib.min())), delta_color="off", border=True)

        left, right = st.columns([1.05, 1])
        with left:
            with st.container(border=True):
                section_header("Total Contribution by Source", "Arithmetic contribution across the full walk-forward period.")
                ordered = contrib.sort_values(ascending=False)
                single_series_bar(ordered, 100.0)
                st.dataframe(ordered.mul(100.0).rename("Total Contribution (%)").to_frame().round(2), use_container_width=True)

        with right:
            with st.container(border=True):
                section_header("Attribution Quality Control", "Daily contributions should reconcile to portfolio returns.")
                if reconciliation <= 1e-8:
                    st.success("Attribution reconciliation: PASS")
                else:
                    st.error("Attribution reconciliation: FAIL")
                st.code(f"{reconciliation:.12f}")
                if report:
                    st.caption(
                        f"Observations: {int(report.get('observation_count', 0)):,} · "
                        f"Transaction cost assumption: {float(report.get('transaction_cost_bps', 0.0)):.1f} bps"
                    )
    else:
        missing_file("attribution_summary.parquet", "python scripts/run_attribution.py")

    if monthly is not None:
        with st.container(border=True):
            section_header("Latest 12 Months of Attribution", "Monthly arithmetic contribution by asset and transaction cost.")
            st.dataframe(monthly.tail(12).astype(float).mul(100.0).round(2), use_container_width=True)


def health_page() -> None:
    page_header(
        "Model Health & Controls",
        "Production controls answer whether Atlas completed correctly, respected portfolio policies, and produced internally consistent outputs.",
        "Operational Monitoring",
    )

    health = load_json("model_health.json")
    if health is None:
        missing_file("model_health.json", "python scripts/run_health.py")
        return

    status = str(health.get("overall_status", "UNKNOWN"))
    status_chip(status)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Checks Passed", str(int(health.get("passed_checks", 0))), border=True)
    c2.metric("Checks Failed", str(int(health.get("failed_checks", 0))), border=True)
    c3.metric("Warnings", str(int(health.get("warning_checks", 0))), border=True)
    c4.metric("Total Controls", str(int(health.get("check_count", 0))), border=True)

    checks = pd.DataFrame(health.get("checks", []))
    with st.container(border=True):
        section_header("Control Register", "Machine-readable checks used to determine overall model health.")
        if not checks.empty:
            cols = [column for column in ["name", "status", "detail"] if column in checks.columns]
            st.dataframe(checks[cols], use_container_width=True, hide_index=True)

    st.caption(f"Health report generated at {health.get('generated_at_utc', 'Unknown')}")
    with st.expander("Raw model_health.json"):
        st.json(health)


def methodology_page() -> None:
    page_header(
        "Methodology & Documentation",
        "Architecture, assumptions, controls, and implementation notes for reviewers who want to inspect how Atlas works.",
        "Model Governance",
    )

    st.markdown(
        """
<div class="atlas-flow">
Market + Macro Data<br>
↓ data quality controls<br>
Momentum + Volatility + Macro Regime<br>
↓ research transformations<br>
Capital Market Assumptions + Covariance<br>
↓ constrained optimization<br>
Target Portfolio + Turnover Controls<br>
↓ walk-forward simulation<br>
Backtest + Attribution + Rebalance Orders<br>
↓ operational checks<br>
Model Health + PM Reporting
</div>
""",
        unsafe_allow_html=True,
    )

    st.divider()
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            section_header("Core Modeling Choices", "Transparent assumptions designed for review.")
            st.markdown(
                """
- **Signals:** 12-1 momentum and rolling annualized volatility.
- **Macro:** growth/inflation directional regime classifier.
- **CMAs:** historical expected-return estimate plus momentum and documented macro tilts.
- **Risk:** annualized historical covariance, cleaned to a positive-semidefinite matrix.
- **Optimization:** long-only mean-variance objective with asset caps, equity cap, cash floor, and turnover controls.
- **Backtest:** monthly walk-forward re-estimation with a conservative macro availability lag.
- **Costs:** transaction costs charged as a function of turnover.
"""
            )

    with right:
        with st.container(border=True):
            section_header("Important Limitations", "What Atlas does not claim.")
            st.markdown(
                """
- This is a **portfolio research demonstration**, not investment advice.
- ETF proxies represent broad asset classes.
- Macro tilts are demonstration priors rather than guaranteed forecasts.
- Historical backtest performance is not evidence of future performance.
- The current data layer is appropriate for a portfolio project, not an institutional market-data license or point-in-time fundamentals warehouse.
- Further productionization would add enterprise data entitlements, orchestration, secrets management, and persistent monitoring infrastructure.
"""
            )

    docs = {
        "Model Specification": load_text("MODEL_SPECIFICATION.md"),
        "Data Dictionary": load_text("DATA_DICTIONARY.md"),
        "AI Engineering Log": load_text("AI_ENGINEERING_LOG.md"),
        "Acceptance Criteria": load_text("STAGE_1_ACCEPTANCE_CRITERIA.md"),
    }
    tabs = st.tabs(list(docs.keys()))
    for tab, (title, content) in zip(tabs, docs.items()):
        with tab:
            if content:
                st.markdown(content)
            else:
                st.caption(f"{title} document not found.")


sidebar_brand()

pages = {
    "Portfolio": [
        st.Page(overview_page, title="Executive Overview", icon=":material/dashboard:", default=True),
        st.Page(portfolio_page, title="Portfolio & Rebalancing", icon=":material/account_balance:"),
    ],
    "Research": [
        st.Page(research_page, title="Research & Signals", icon=":material/monitoring:"),
        st.Page(backtest_page, title="Walk-Forward Backtest", icon=":material/query_stats:"),
        st.Page(attribution_page, title="Attribution", icon=":material/pie_chart:"),
    ],
    "Operations": [
        st.Page(health_page, title="Model Health", icon=":material/health_and_safety:"),
        st.Page(methodology_page, title="Methodology", icon=":material/description:"),
    ],
}

navigation = st.navigation(pages)
navigation.run()

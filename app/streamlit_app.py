from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from atlas.config import load_yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DATA = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

DEMO_DATA = (
    PROJECT_ROOT
    / "data"
    / "demo"
)

DOCS = (
    PROJECT_ROOT
    / "docs"
)


def resolve_data_directory() -> Path:
    """Use live local outputs when available, otherwise public demo data."""

    required = (
        PROCESSED_DATA
        / "optimized_weights.parquet"
    )

    if required.exists():
        return PROCESSED_DATA

    return DEMO_DATA


DATA = resolve_data_directory()


PALETTES = {
    "Aurora": {
        "accent": "#7C3AED",
        "accent_2": "#06B6D4",
        "accent_3": "#22C55E",
        "warm": "#F59E0B",
        "hot": "#EC4899",
        "danger": "#F43F5E",
        "ink": "#172033",
        "muted": "#64748B",
        "soft": "#F5F3FF",
        "series": [
            "#7C3AED",
            "#06B6D4",
            "#22C55E",
            "#F59E0B",
            "#EC4899",
            "#3B82F6",
            "#F43F5E",
        ],
    },
    "Ocean": {
        "accent": "#0F766E",
        "accent_2": "#0EA5E9",
        "accent_3": "#14B8A6",
        "warm": "#F59E0B",
        "hot": "#8B5CF6",
        "danger": "#F43F5E",
        "ink": "#172033",
        "muted": "#64748B",
        "soft": "#ECFEFF",
        "series": [
            "#0F766E",
            "#0EA5E9",
            "#14B8A6",
            "#F59E0B",
            "#8B5CF6",
            "#2563EB",
            "#F43F5E",
        ],
    },
    "Sunset": {
        "accent": "#EA580C",
        "accent_2": "#F59E0B",
        "accent_3": "#DB2777",
        "warm": "#EAB308",
        "hot": "#7C3AED",
        "danger": "#E11D48",
        "ink": "#231F20",
        "muted": "#6B7280",
        "soft": "#FFF7ED",
        "series": [
            "#EA580C",
            "#F59E0B",
            "#DB2777",
            "#7C3AED",
            "#0EA5E9",
            "#22C55E",
            "#E11D48",
        ],
    },
    "Candy": {
        "accent": "#DB2777",
        "accent_2": "#8B5CF6",
        "accent_3": "#06B6D4",
        "warm": "#F59E0B",
        "hot": "#F43F5E",
        "danger": "#DC2626",
        "ink": "#25182C",
        "muted": "#6B6472",
        "soft": "#FDF2F8",
        "series": [
            "#DB2777",
            "#8B5CF6",
            "#06B6D4",
            "#F59E0B",
            "#22C55E",
            "#3B82F6",
            "#F43F5E",
        ],
    },
}


st.set_page_config(
    page_title="Atlas | Multi-Asset Research Platform",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_parquet(
    filename: str,
) -> pd.DataFrame | None:
    path = DATA / filename

    if not path.exists():
        return None

    return pd.read_parquet(
        path
    )


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


@st.cache_data
def load_text(
    filename: str,
) -> str | None:
    path = DOCS / filename

    if not path.exists():
        return None

    return path.read_text(
        encoding="utf-8"
    )


@st.cache_data
def load_portfolio_config() -> dict:
    return load_yaml(
        str(
            PROJECT_ROOT
            / "configs"
            / "portfolio.yaml"
        )
    )


def inject_css(
    palette: dict[str, object],
) -> None:
    accent = str(
        palette["accent"]
    )

    accent_2 = str(
        palette["accent_2"]
    )

    hot = str(
        palette["hot"]
    )

    ink = str(
        palette["ink"]
    )

    muted = str(
        palette["muted"]
    )

    st.markdown(
        f"""
        <style>
        :root {{
            --atlas-accent: {accent};
            --atlas-accent-2: {accent_2};
            --atlas-hot: {hot};
            --atlas-ink: {ink};
            --atlas-muted: {muted};
        }}

        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1550px;
        }}

        [data-testid="stSidebar"] {{
            border-right:
                1px solid rgba(
                    148,
                    163,
                    184,
                    0.18
                );
        }}

        .atlas-hero {{
            padding: 1.25rem 1.35rem;
            border-radius: 1.25rem;
            color: white;
            background:
                radial-gradient(
                    circle at 15% 20%,
                    {accent_2}55 0,
                    transparent 28%
                ),
                radial-gradient(
                    circle at 88% 15%,
                    {hot}55 0,
                    transparent 24%
                ),
                linear-gradient(
                    120deg,
                    {accent},
                    {accent_2}
                );
            margin-bottom: 1rem;
            overflow: hidden;
            position: relative;
        }}

        .atlas-hero::after {{
            content: "";
            position: absolute;
            width: 180px;
            height: 180px;
            border-radius: 999px;
            border:
                1px solid
                rgba(
                    255,
                    255,
                    255,
                    .28
                );
            right: -45px;
            bottom: -85px;
        }}

        .atlas-eyebrow {{
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
            opacity: .85;
            margin-bottom: .35rem;
        }}

        .atlas-title {{
            font-size: 2.15rem;
            font-weight: 800;
            letter-spacing: -.035em;
            line-height: 1.05;
            margin-bottom: .35rem;
        }}

        .atlas-subtitle {{
            max-width: 850px;
            opacity: .92;
            font-size: .96rem;
        }}

        .atlas-chip {{
            display: inline-block;
            margin-top: .8rem;
            margin-right: .35rem;
            padding: .28rem .62rem;
            border-radius: 999px;
            background:
                rgba(
                    255,
                    255,
                    255,
                    .16
                );
            border:
                1px solid
                rgba(
                    255,
                    255,
                    255,
                    .22
                );
            font-size: .75rem;
            font-weight: 700;
        }}

        .atlas-section {{
            font-size: 1.08rem;
            font-weight: 800;
            letter-spacing: -.01em;
            color: var(--atlas-ink);
            margin-bottom: .1rem;
        }}

        .atlas-note {{
            font-size: .82rem;
            color: var(--atlas-muted);
            margin-bottom: .55rem;
        }}

        .atlas-callout {{
            border-left:
                5px solid
                var(--atlas-accent);
            background:
                rgba(
                    124,
                    58,
                    237,
                    .06
                );
            border-radius: 1rem;
            padding: .9rem 1rem;
            margin: .75rem 0;
        }}

        .atlas-flow {{
            font-family:
                ui-monospace,
                SFMono-Regular,
                Menlo,
                Monaco,
                Consolas,
                monospace;
            padding: 1rem 1.1rem;
            border-radius: 1rem;
            color: #F8FAFC;
            background:
                linear-gradient(
                    135deg,
                    #111827,
                    #1E293B
                );
            border:
                1px solid
                rgba(
                    255,
                    255,
                    255,
                    .08
                );
            line-height: 1.75;
        }}

        div[data-testid="stMetric"] {{
            border-top:
                4px solid
                var(--atlas-accent)
                !important;
            transition:
                transform .18s ease,
                box-shadow .18s ease;
        }}

        div[data-testid="stMetric"]:hover {{
            transform: translateY(-3px);
            box-shadow:
                0 12px 30px
                rgba(
                    15,
                    23,
                    42,
                    .10
                );
        }}

        [data-testid="stDataFrame"] {{
            border-radius: .85rem;
            overflow: hidden;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: .35rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 999px;
            padding-left: .8rem;
            padding-right: .8rem;
        }}

        button[kind="secondary"],
        button[kind="primary"] {{
            transition:
                transform .15s ease;
        }}

        button[kind="secondary"]:hover,
        button[kind="primary"]:hover {{
            transform:
                translateY(-1px);
        }}

        @media (max-width: 700px) {{
            .atlas-title {{
                font-size: 1.65rem;
            }}

            .atlas-hero {{
                padding: 1rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(
    title: str,
    subtitle: str,
    *,
    eyebrow: str,
    chips: list[str] | None = None,
) -> None:
    chip_html = "".join(
        (
            '<span class="atlas-chip">'
            f"{chip}"
            "</span>"
        )
        for chip in (
            chips
            or []
        )
    )

    st.markdown(
        f"""
        <div class="atlas-hero">
            <div class="atlas-eyebrow">
                {eyebrow}
            </div>

            <div class="atlas-title">
                {title}
            </div>

            <div class="atlas-subtitle">
                {subtitle}
            </div>

            <div>
                {chip_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(
    title: str,
    note: str | None = None,
) -> None:
    st.markdown(
        (
            '<div class="atlas-section">'
            f"{title}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if note:
        st.markdown(
            (
                '<div class="atlas-note">'
                f"{note}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def missing_file(
    filename: str,
    command: str | None = None,
) -> None:
    st.info(
        f"`{filename}` has not been generated yet."
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


def format_number(
    value: float,
    decimals: int = 2,
) -> str:
    return f"{value:.{decimals}f}"


def latest_macro_regime() -> str | None:
    frame = load_parquet(
        "macro_regimes.parquet"
    )

    if (
        frame is None
        or "macro_regime"
        not in frame.columns
    ):
        return None

    series = frame[
        "macro_regime"
    ].dropna()

    if series.empty:
        return None

    return str(
        series.iloc[-1]
    )


def formatted_regime(
    regime: str | None,
) -> str:
    if not regime:
        return "Unavailable"

    return (
        regime
        .replace(
            "_",
            " ",
        )
        .title()
    )


def latest_market_date() -> str | None:
    prices = load_parquet(
        "market_prices.parquet"
    )

    if (
        prices is None
        or prices.empty
    ):
        return None

    value = prices.index.max()

    if hasattr(
        value,
        "date",
    ):
        return str(
            value.date()
        )

    return str(value)


def color_series_frame(
    series: pd.Series,
    *,
    multiplier: float = 1.0,
) -> pd.DataFrame:
    frame = (
        series
        .astype(float)
        .mul(multiplier)
        .rename("Value")
        .rename_axis("Asset")
        .reset_index()
    )

    frame["Asset"] = (
        frame["Asset"]
        .astype(str)
    )

    return frame


def colorful_bar(
    series: pd.Series,
    palette: dict[str, object],
    *,
    multiplier: float = 1.0,
) -> None:
    frame = color_series_frame(
        series,
        multiplier=multiplier,
    )

    spec = {
        "mark": {
            "type": "bar",
            "cornerRadiusTopLeft": 7,
            "cornerRadiusTopRight": 7,
            "cursor": "pointer",
        },
        "encoding": {
            "x": {
                "field": "Asset",
                "type": "nominal",
                "sort": None,
                "axis": {
                    "title": None,
                    "labelAngle": 0,
                },
            },
            "y": {
                "field": "Value",
                "type": "quantitative",
                "axis": {
                    "title": None,
                },
            },
            "color": {
                "field": "Asset",
                "type": "nominal",
                "scale": {
                    "range": list(
                        palette["series"]
                    ),
                },
                "legend": None,
            },
            "tooltip": [
                {
                    "field": "Asset",
                    "type": "nominal",
                },
                {
                    "field": "Value",
                    "type": "quantitative",
                    "format": ".2f",
                },
            ],
        },
        "height": 320,
    }

    st.vega_lite_chart(
        frame,
        spec,
        use_container_width=True,
    )


def donut_chart(
    weights: pd.Series,
    palette: dict[str, object],
) -> None:
    frame = color_series_frame(
        weights,
        multiplier=100.0,
    )

    spec = {
        "mark": {
            "type": "arc",
            "innerRadius": 65,
            "outerRadius": 125,
            "cornerRadius": 4,
            "padAngle": 0.015,
            "cursor": "pointer",
        },
        "encoding": {
            "theta": {
                "field": "Value",
                "type": "quantitative",
            },
            "color": {
                "field": "Asset",
                "type": "nominal",
                "scale": {
                    "range": list(
                        palette["series"]
                    ),
                },
                "legend": {
                    "orient": "bottom",
                    "title": None,
                },
            },
            "tooltip": [
                {
                    "field": "Asset",
                    "type": "nominal",
                },
                {
                    "field": "Value",
                    "type": "quantitative",
                    "format": ".2f",
                },
            ],
        },
        "height": 340,
    }

    st.vega_lite_chart(
        frame,
        spec,
        use_container_width=True,
    )


def performance_line_chart(
    returns: pd.DataFrame,
    palette: dict[str, object],
    window: str,
) -> None:
    clean = (
        returns
        .copy()
        .dropna(
            how="all"
        )
    )

    if clean.empty:
        return

    if window != "All":
        days = {
            "1Y": 365,
            "3Y": 365 * 3,
            "5Y": 365 * 5,
        }[window]

        cutoff = (
            clean.index.max()
            - pd.Timedelta(
                days=days
            )
        )

        clean = clean.loc[
            clean.index
            >= cutoff
        ]

    wealth = (
        1.0
        + clean.fillna(0.0)
    ).cumprod()

    long = (
        wealth
        .rename_axis("Date")
        .reset_index()
        .melt(
            id_vars="Date",
            var_name="Strategy",
            value_name="Growth",
        )
    )

    spec = {
        "mark": {
            "type": "line",
            "strokeWidth": 3,
        },
        "encoding": {
            "x": {
                "field": "Date",
                "type": "temporal",
                "axis": {
                    "title": None,
                },
            },
            "y": {
                "field": "Growth",
                "type": "quantitative",
                "axis": {
                    "title": "Growth of $1",
                },
                "scale": {
                    "zero": False,
                },
            },
            "color": {
                "field": "Strategy",
                "type": "nominal",
                "scale": {
                    "range": list(
                        palette["series"]
                    ),
                },
                "legend": {
                    "orient": "bottom",
                    "title": None,
                },
            },
            "tooltip": [
                {
                    "field": "Date",
                    "type": "temporal",
                },
                {
                    "field": "Strategy",
                    "type": "nominal",
                },
                {
                    "field": "Growth",
                    "type": "quantitative",
                    "format": ".3f",
                },
            ],
        },
        "height": 390,
    }

    st.vega_lite_chart(
        long,
        spec,
        use_container_width=True,
    )


def allocation_table(
    weights: pd.Series,
) -> pd.DataFrame:
    return (
        weights
        .astype(float)
        .mul(100.0)
        .rename(
            "Target Weight (%)"
        )
        .to_frame()
        .round(2)
    )


def overview_page(
    palette: dict[str, object],
) -> None:
    health = load_json(
        "model_health.json"
    )

    metrics = load_json(
        "backtest_metrics.json"
    )

    weights_frame = load_parquet(
        "optimized_weights.parquet"
    )

    attribution = load_parquet(
        "attribution_summary.parquet"
    )

    turnover = load_parquet(
        "backtest_turnover.parquet"
    )

    rebalance = load_parquet(
        "rebalance_orders.parquet"
    )

    regime = latest_macro_regime()

    page_header(
        "Atlas Portfolio Command Center",
        (
            "Explore the latest portfolio, model state, "
            "market regime, risk-adjusted performance, "
            "and live rebalance workflow."
        ),
        eyebrow=(
            "Multi-Asset Portfolio Intelligence"
        ),
        chips=[
            f"🌎 {formatted_regime(regime)}",
            "🧠 Systematic Research",
            "🛡️ Constraint Aware",
        ],
    )

    atlas: dict = {}

    if metrics:
        atlas = metrics.get(
            "atlas",
            {},
        )

    passed = (
        int(
            health.get(
                "passed_checks",
                0,
            )
        )
        if health
        else 0
    )

    total = (
        int(
            health.get(
                "check_count",
                0,
            )
        )
        if health
        else 0
    )

    kpis = st.columns(
        6,
        border=True,
    )

    with kpis[0]:
        st.metric(
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

    with kpis[1]:
        st.metric(
            "Sharpe Ratio",
            format_number(
                float(
                    atlas.get(
                        "sharpe_ratio",
                        0.0,
                    )
                )
            ),
        )

    with kpis[2]:
        st.metric(
            "Volatility",
            format_percent(
                float(
                    atlas.get(
                        "annualized_volatility",
                        0.0,
                    )
                )
            ),
        )

    with kpis[3]:
        st.metric(
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

    with kpis[4]:
        st.metric(
            "Macro Regime",
            formatted_regime(
                regime
            ),
        )

    with kpis[5]:
        st.metric(
            "Health Checks",
            (
                f"{passed}/{total}"
                if total
                else "—"
            ),
        )

    st.write("")

    focus = st.segmented_control(
        "Explore",
        [
            "Allocation",
            "Performance",
            "Operations",
        ],
        default="Allocation",
        label_visibility="collapsed",
    )

    if focus == "Allocation":
        columns = st.columns(
            [
                1.05,
                1,
            ],
            border=True,
        )

        with columns[0]:
            section_header(
                "Target Portfolio",
                (
                    "Hover the chart to inspect "
                    "target weights."
                ),
            )

            if (
                weights_frame
                is not None
                and "weight"
                in weights_frame.columns
            ):
                weights = (
                    weights_frame[
                        "weight"
                    ]
                    .astype(float)
                    .sort_values(
                        ascending=False
                    )
                )

                donut_chart(
                    weights,
                    palette,
                )

            else:
                missing_file(
                    "optimized_weights.parquet",
                    "python scripts/run_stage1.py",
                )

        with columns[1]:
            section_header(
                "Portfolio Snapshot",
                (
                    "A quick PM-style read "
                    "of current positioning."
                ),
            )

            if (
                weights_frame
                is not None
                and "weight"
                in weights_frame.columns
            ):
                weights = (
                    weights_frame[
                        "weight"
                    ]
                    .astype(float)
                )

                equity = float(
                    weights
                    .reindex(
                        [
                            "SPY",
                            "VXUS",
                        ]
                    )
                    .fillna(0.0)
                    .sum()
                )

                cash = float(
                    weights.get(
                        "BIL",
                        0.0,
                    )
                )

                largest = str(
                    weights.idxmax()
                )

                snapshot = st.columns(
                    2,
                    border=True,
                )

                with snapshot[0]:
                    st.metric(
                        "Equity",
                        format_percent(
                            equity
                        ),
                    )

                    st.metric(
                        "Cash",
                        format_percent(
                            cash
                        ),
                    )

                with snapshot[1]:
                    st.metric(
                        "Largest Position",
                        (
                            f"{largest} · "
                            f"{format_percent(float(weights.max()))}"
                        ),
                    )

                    st.metric(
                        "Assets",
                        str(
                            len(weights)
                        ),
                    )

                st.dataframe(
                    allocation_table(
                        weights.sort_values(
                            ascending=False
                        )
                    ),
                    use_container_width=True,
                )

    elif focus == "Performance":
        section_header(
            "Growth of $1",
            (
                "Interactive benchmark comparison "
                "from the walk-forward backtest."
            ),
        )

        returns = load_parquet(
            "backtest_returns.parquet"
        )

        if returns is None:
            missing_file(
                "backtest_returns.parquet",
                "python scripts/run_backtest.py",
            )

        else:
            window = st.segmented_control(
                "Window",
                [
                    "1Y",
                    "3Y",
                    "5Y",
                    "All",
                ],
                default="All",
            )

            performance_line_chart(
                returns,
                palette,
                str(window),
            )

    else:
        columns = st.columns(
            3,
            border=True,
        )

        with columns[0]:
            section_header(
                "Trading Activity"
            )

            if (
                turnover
                is not None
                and "turnover"
                in turnover.columns
            ):
                series = (
                    turnover[
                        "turnover"
                    ]
                    .astype(float)
                )

                st.metric(
                    "Average Turnover",
                    format_percent(
                        float(
                            series.mean()
                        )
                    ),
                )

                st.metric(
                    "Maximum Turnover",
                    format_percent(
                        float(
                            series.max()
                        )
                    ),
                )

        with columns[1]:
            section_header(
                "Rebalance Orders"
            )

            if (
                rebalance
                is not None
                and "action"
                in rebalance.columns
            ):
                actions = (
                    rebalance[
                        "action"
                    ]
                    .astype(str)
                )

                st.metric(
                    "BUY",
                    str(
                        int(
                            (
                                actions
                                == "BUY"
                            ).sum()
                        )
                    ),
                )

                st.metric(
                    "SELL",
                    str(
                        int(
                            (
                                actions
                                == "SELL"
                            ).sum()
                        )
                    ),
                )

                st.metric(
                    "HOLD",
                    str(
                        int(
                            (
                                actions
                                == "HOLD"
                            ).sum()
                        )
                    ),
                )

            else:
                st.caption(
                    "Generate rebalance orders to populate."
                )

        with columns[2]:
            section_header(
                "Top Attribution"
            )

            if (
                attribution
                is not None
                and "total_contribution"
                in attribution.columns
                and not attribution.empty
            ):
                contribution = (
                    attribution[
                        "total_contribution"
                    ]
                    .astype(float)
                )

                st.metric(
                    "Top Contributor",
                    str(
                        contribution.idxmax()
                    ),
                    format_percent(
                        float(
                            contribution.max()
                        )
                    ),
                )

                st.metric(
                    "Largest Detractor",
                    str(
                        contribution.idxmin()
                    ),
                    format_percent(
                        float(
                            contribution.min()
                        )
                    ),
                )

    if health:
        status = str(
            health.get(
                "overall_status",
                "UNKNOWN",
            )
        )

        if status == "HEALTHY":
            icon = "🟢"

        elif status == "WARNING":
            icon = "🟠"

        else:
            icon = "🔴"

        st.markdown(
            (
                '<div class="atlas-callout">'
                f"<b>{icon} Model status: {status}</b><br>"
                "Atlas combines research outputs with "
                "explicit portfolio controls, "
                "reconciliation checks, and "
                "operational monitoring."
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def research_page(
    palette: dict[str, object],
) -> None:
    page_header(
        "Research Playground",
        (
            "Move between signals, macro conditions, "
            "and capital market assumptions to see "
            "what is driving the portfolio."
        ),
        eyebrow="Quant Research",
        chips=[
            "📡 Momentum",
            "🌡️ Volatility",
            "🌎 Macro",
            "🎯 CMAs",
        ],
    )

    view = st.segmented_control(
        "Research view",
        [
            "Momentum",
            "Volatility",
            "Macro",
            "CMAs",
        ],
        default="Momentum",
    )

    if view == "Momentum":
        momentum = load_parquet(
            "momentum_zscore.parquet"
        )

        if (
            momentum is None
            or momentum
            .dropna(
                how="all"
            )
            .empty
        ):
            missing_file(
                "momentum_zscore.parquet"
            )
            return

        latest = (
            momentum
            .dropna(
                how="all"
            )
            .iloc[-1]
            .dropna()
            .astype(float)
            .sort_values(
                ascending=False
            )
        )

        columns = st.columns(
            [
                1.3,
                1,
            ],
            border=True,
        )

        with columns[0]:
            section_header(
                "Momentum Leaderboard",
                (
                    "Latest cross-sectional "
                    "12-1 momentum z-scores."
                ),
            )

            colorful_bar(
                latest,
                palette,
            )

        with columns[1]:
            section_header(
                "Signal Table"
            )

            st.dataframe(
                latest
                .rename(
                    "Momentum Z-Score"
                )
                .to_frame()
                .round(3),
                use_container_width=True,
            )

    elif view == "Volatility":
        volatility = load_parquet(
            "volatility.parquet"
        )

        if (
            volatility is None
            or volatility
            .dropna(
                how="all"
            )
            .empty
        ):
            missing_file(
                "volatility.parquet"
            )
            return

        latest = (
            volatility
            .dropna(
                how="all"
            )
            .iloc[-1]
            .dropna()
            .astype(float)
            .sort_values(
                ascending=False
            )
        )

        columns = st.columns(
            [
                1.3,
                1,
            ],
            border=True,
        )

        with columns[0]:
            section_header(
                "Risk Landscape",
                (
                    "Latest annualized rolling "
                    "volatility by asset."
                ),
            )

            colorful_bar(
                latest,
                palette,
                multiplier=100.0,
            )

        with columns[1]:
            section_header(
                "Risk Table"
            )

            st.dataframe(
                latest
                .mul(100.0)
                .rename(
                    "Annualized Volatility (%)"
                )
                .to_frame()
                .round(2),
                use_container_width=True,
            )

    elif view == "Macro":
        features = load_parquet(
            "macro_features.parquet"
        )

        regimes = load_parquet(
            "macro_regimes.parquet"
        )

        top = st.columns(
            3,
            border=True,
        )

        regime = latest_macro_regime()

        with top[0]:
            st.metric(
                "Current Regime",
                formatted_regime(
                    regime
                ),
            )

        if (
            features
            is not None
            and not features
            .dropna(
                how="all"
            )
            .empty
        ):
            latest = (
                features
                .dropna(
                    how="all"
                )
                .iloc[-1]
            )

            with top[1]:
                st.metric(
                    "Inflation YoY",
                    (
                        f"{float(latest.get('inflation_yoy', 0.0)):.2f}%"
                    ),
                )

            with top[2]:
                st.metric(
                    "Growth YoY",
                    (
                        f"{float(latest.get('growth_yoy', 0.0)):.2f}%"
                    ),
                )

            section_header(
                "Macro Feature History",
                (
                    "Hover to inspect the growth "
                    "and inflation feature paths."
                ),
            )

            chart_columns = [
                column
                for column in [
                    "inflation_yoy",
                    "growth_yoy",
                ]
                if column
                in features.columns
            ]

            if chart_columns:
                chart = (
                    features[
                        chart_columns
                    ]
                    .dropna(
                        how="all"
                    )
                    .rename_axis(
                        "Date"
                    )
                    .reset_index()
                    .melt(
                        id_vars="Date",
                        var_name="Feature",
                        value_name="Value",
                    )
                )

                spec = {
                    "mark": {
                        "type": "line",
                        "strokeWidth": 2.5,
                    },
                    "encoding": {
                        "x": {
                            "field": "Date",
                            "type": "temporal",
                            "axis": {
                                "title": None,
                            },
                        },
                        "y": {
                            "field": "Value",
                            "type": "quantitative",
                            "axis": {
                                "title": None,
                            },
                        },
                        "color": {
                            "field": "Feature",
                            "type": "nominal",
                            "scale": {
                                "range": list(
                                    palette[
                                        "series"
                                    ]
                                ),
                            },
                            "legend": {
                                "orient": "bottom",
                                "title": None,
                            },
                        },
                        "tooltip": [
                            {
                                "field": "Date",
                                "type": "temporal",
                            },
                            {
                                "field": "Feature",
                                "type": "nominal",
                            },
                            {
                                "field": "Value",
                                "type": "quantitative",
                                "format": ".2f",
                            },
                        ],
                    },
                    "height": 380,
                }

                st.vega_lite_chart(
                    chart,
                    spec,
                    use_container_width=True,
                )

        if (
            regimes is not None
            and "macro_regime"
            in regimes.columns
        ):
            with st.expander(
                "Recent regime history"
            ):
                st.dataframe(
                    regimes[
                        [
                            "macro_regime"
                        ]
                    ]
                    .dropna()
                    .tail(18),
                    use_container_width=True,
                )

    else:
        cma = load_parquet(
            "cma_regime_adjusted.parquet"
        )

        if cma is None:
            missing_file(
                "cma_regime_adjusted.parquet",
                "python scripts/run_stage1.py",
            )
            return

        section_header(
            "Regime-Adjusted Expected Returns",
            (
                "The portfolio optimizer consumes "
                "these expected returns."
            ),
        )

        if (
            "regime_adjusted_expected_return"
            in cma.columns
        ):
            series = (
                cma[
                    "regime_adjusted_expected_return"
                ]
                .astype(float)
                .sort_values(
                    ascending=False
                )
            )

            colorful_bar(
                series,
                palette,
                multiplier=100.0,
            )

        with st.expander(
            "View complete CMA table",
            expanded=True,
        ):
            st.dataframe(
                cma
                .astype(float)
                .mul(100.0)
                .round(2),
                use_container_width=True,
            )


def portfolio_page(
    palette: dict[str, object],
) -> None:
    page_header(
        "Portfolio Lab",
        (
            "Inspect target weights, constraint utilization, "
            "and the trading plan that moves current holdings "
            "toward the latest model portfolio."
        ),
        eyebrow="Portfolio Construction",
        chips=[
            "⚖️ Constrained",
            "💵 Cash Floor",
            "🔄 Turnover Aware",
        ],
    )

    target = load_parquet(
        "optimized_weights.parquet"
    )

    baseline = load_parquet(
        "baseline_weights.parquet"
    )

    rebalance = load_parquet(
        "rebalance_orders.parquet"
    )

    if (
        target is None
        or "weight"
        not in target.columns
    ):
        missing_file(
            "optimized_weights.parquet",
            "python scripts/run_stage1.py",
        )
        return

    weights = (
        target[
            "weight"
        ]
        .astype(float)
    )

    settings = (
        load_portfolio_config()
        .get(
            "portfolio",
            {},
        )
    )

    equity = float(
        weights
        .reindex(
            [
                "SPY",
                "VXUS",
            ]
        )
        .fillna(0.0)
        .sum()
    )

    cash = float(
        weights.get(
            "BIL",
            0.0,
        )
    )

    equity_cap = float(
        settings.get(
            "max_equity_weight",
            0.60,
        )
    )

    cash_floor = float(
        settings.get(
            "min_cash_weight",
            0.02,
        )
    )

    turnover_limit = float(
        settings.get(
            "max_turnover_per_rebalance",
            0.20,
        )
    )

    metrics = st.columns(
        4,
        border=True,
    )

    with metrics[0]:
        st.metric(
            "Equity Exposure",
            format_percent(
                equity
            ),
            (
                f"Cap "
                f"{format_percent(equity_cap)}"
            ),
            delta_color="off",
        )

    with metrics[1]:
        st.metric(
            "Cash",
            format_percent(
                cash
            ),
            (
                f"Floor "
                f"{format_percent(cash_floor)}"
            ),
            delta_color="off",
        )

    with metrics[2]:
        st.metric(
            "Largest Position",
            (
                f"{weights.idxmax()} · "
                f"{format_percent(float(weights.max()))}"
            ),
        )

    with metrics[3]:
        st.metric(
            "Turnover Policy",
            format_percent(
                turnover_limit
            ),
        )

    tab1, tab2, tab3 = st.tabs(
        [
            "🎯 Target Portfolio",
            "🧾 Rebalance Orders",
            "🛡️ Constraints",
        ]
    )

    with tab1:
        columns = st.columns(
            [
                1,
                1.2,
            ],
            border=True,
        )

        with columns[0]:
            section_header(
                "Portfolio Mix"
            )

            donut_chart(
                weights.sort_values(
                    ascending=False
                ),
                palette,
            )

        with columns[1]:
            section_header(
                "Target vs Equal Weight"
            )

            comparison = target.rename(
                columns={
                    "weight": "Atlas Target"
                }
            )

            if (
                baseline is not None
                and "weight"
                in baseline.columns
            ):
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
                .astype(float)
                .mul(100.0)
            )

            long = (
                comparison
                .rename_axis(
                    "Asset"
                )
                .reset_index()
                .melt(
                    id_vars="Asset",
                    var_name="Portfolio",
                    value_name="Weight",
                )
            )

            spec = {
                "mark": {
                    "type": "bar",
                    "cornerRadiusTopLeft": 5,
                    "cornerRadiusTopRight": 5,
                },
                "encoding": {
                    "x": {
                        "field": "Asset",
                        "type": "nominal",
                        "axis": {
                            "title": None,
                        },
                    },
                    "y": {
                        "field": "Weight",
                        "type": "quantitative",
                        "axis": {
                            "title": "Weight (%)",
                        },
                    },
                    "xOffset": {
                        "field": "Portfolio",
                    },
                    "color": {
                        "field": "Portfolio",
                        "type": "nominal",
                        "scale": {
                            "range": list(
                                palette[
                                    "series"
                                ]
                            ),
                        },
                        "legend": {
                            "orient": "bottom",
                            "title": None,
                        },
                    },
                    "tooltip": [
                        {
                            "field": "Asset",
                            "type": "nominal",
                        },
                        {
                            "field": "Portfolio",
                            "type": "nominal",
                        },
                        {
                            "field": "Weight",
                            "type": "quantitative",
                            "format": ".2f",
                        },
                    ],
                },
                "height": 340,
            }

            st.vega_lite_chart(
                long,
                spec,
                use_container_width=True,
            )

    with tab2:
        if rebalance is None:
            missing_file(
                "rebalance_orders.parquet",
                "python scripts/generate_rebalance.py",
            )

        else:
            action_filter = st.multiselect(
                "Show actions",
                [
                    "BUY",
                    "SELL",
                    "HOLD",
                ],
                default=[
                    "BUY",
                    "SELL",
                    "HOLD",
                ],
            )

            display = rebalance.copy()

            if (
                "action"
                in display.columns
            ):
                display = display[
                    display[
                        "action"
                    ]
                    .astype(str)
                    .isin(
                        action_filter
                    )
                ]

            st.dataframe(
                display,
                use_container_width=True,
            )

            if (
                "action"
                in rebalance.columns
            ):
                counts = (
                    rebalance[
                        "action"
                    ]
                    .astype(str)
                    .value_counts()
                )

                cards = st.columns(
                    3,
                    border=True,
                )

                with cards[0]:
                    st.metric(
                        "BUY",
                        str(
                            int(
                                counts.get(
                                    "BUY",
                                    0,
                                )
                            )
                        ),
                    )

                with cards[1]:
                    st.metric(
                        "SELL",
                        str(
                            int(
                                counts.get(
                                    "SELL",
                                    0,
                                )
                            )
                        ),
                    )

                with cards[2]:
                    st.metric(
                        "HOLD",
                        str(
                            int(
                                counts.get(
                                    "HOLD",
                                    0,
                                )
                            )
                        ),
                    )

    with tab3:
        checks = pd.DataFrame(
            [
                {
                    "Rule": "Maximum equity",
                    "Current": equity,
                    "Limit": equity_cap,
                    "Status": (
                        "PASS"
                        if equity
                        <= equity_cap
                        + 1e-6
                        else "FAIL"
                    ),
                },
                {
                    "Rule": "Minimum cash",
                    "Current": cash,
                    "Limit": cash_floor,
                    "Status": (
                        "PASS"
                        if cash
                        + 1e-6
                        >= cash_floor
                        else "FAIL"
                    ),
                },
                {
                    "Rule": "Fully invested",
                    "Current": float(
                        weights.sum()
                    ),
                    "Limit": 1.0,
                    "Status": (
                        "PASS"
                        if abs(
                            float(
                                weights.sum()
                            )
                            - 1.0
                        )
                        <= 1e-6
                        else "FAIL"
                    ),
                },
            ]
        )

        pretty = checks.copy()

        pretty[
            "Current"
        ] = pretty[
            "Current"
        ].map(
            format_percent
        )

        pretty[
            "Limit"
        ] = pretty[
            "Limit"
        ].map(
            format_percent
        )

        st.dataframe(
            pretty,
            use_container_width=True,
            hide_index=True,
        )


def backtest_page(
    palette: dict[str, object],
) -> None:
    page_header(
        "Backtest Arcade",
        (
            "Explore walk-forward performance, "
            "benchmark competition, turnover, "
            "and recent historical allocations."
        ),
        eyebrow="Model Validation",
        chips=[
            "🕒 Walk Forward",
            "💸 Costs Included",
            "🚫 No Look-Ahead",
        ],
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

    weights = load_parquet(
        "backtest_weights.parquet"
    )

    if returns is None:
        missing_file(
            "backtest_returns.parquet",
            "python scripts/run_backtest.py",
        )
        return

    window = st.segmented_control(
        "Performance window",
        [
            "1Y",
            "3Y",
            "5Y",
            "All",
        ],
        default="All",
    )

    performance_line_chart(
        returns,
        palette,
        str(window),
    )

    rows: dict[
        str,
        dict[str, str],
    ] = {}

    if metrics:
        mapping = {
            "atlas": "🪐 Atlas",
            "equal_weight": (
                "⚖️ Equal Weight"
            ),
            "sixty_forty": (
                "🏛️ 60/40"
            ),
        }

        for (
            key,
            label,
        ) in mapping.items():
            values = metrics.get(
                key
            )

            if not values:
                continue

            rows[
                label
            ] = {
                "Annualized Return": (
                    format_percent(
                        float(
                            values.get(
                                "annualized_return",
                                0.0,
                            )
                        )
                    )
                ),
                "Volatility": (
                    format_percent(
                        float(
                            values.get(
                                "annualized_volatility",
                                0.0,
                            )
                        )
                    )
                ),
                "Sharpe": (
                    format_number(
                        float(
                            values.get(
                                "sharpe_ratio",
                                0.0,
                            )
                        )
                    )
                ),
                "Max Drawdown": (
                    format_percent(
                        float(
                            values.get(
                                "max_drawdown",
                                0.0,
                            )
                        )
                    )
                ),
            }

    if rows:
        section_header(
            "Scoreboard",
            (
                "Risk-adjusted performance over "
                "the common backtest window."
            ),
        )

        st.dataframe(
            pd.DataFrame(
                rows
            ).T,
            use_container_width=True,
        )

    columns = st.columns(
        [
            1.2,
            1,
        ],
        border=True,
    )

    with columns[0]:
        section_header(
            "Turnover Trail"
        )

        if (
            turnover
            is not None
            and "turnover"
            in turnover.columns
        ):
            series = (
                turnover[
                    "turnover"
                ]
                .astype(float)
            )

            chart = (
                series
                .mul(100.0)
                .rename(
                    "Turnover"
                )
                .rename_axis(
                    "Date"
                )
                .reset_index()
            )

            spec = {
                "mark": {
                    "type": "area",
                    "line": {
                        "color": str(
                            palette[
                                "accent"
                            ]
                        ),
                    },
                    "color": {
                        "gradient": (
                            "linear"
                        ),
                        "x1": 0,
                        "y1": 0,
                        "x2": 0,
                        "y2": 1,
                        "stops": [
                            {
                                "offset": 0,
                                "color": str(
                                    palette[
                                        "accent"
                                    ]
                                ),
                            },
                            {
                                "offset": 1,
                                "color": str(
                                    palette[
                                        "accent_2"
                                    ]
                                ),
                            },
                        ],
                    },
                    "opacity": 0.55,
                },
                "encoding": {
                    "x": {
                        "field": "Date",
                        "type": "temporal",
                        "axis": {
                            "title": None,
                        },
                    },
                    "y": {
                        "field": "Turnover",
                        "type": "quantitative",
                        "axis": {
                            "title": (
                                "Turnover (%)"
                            ),
                        },
                    },
                    "tooltip": [
                        {
                            "field": "Date",
                            "type": "temporal",
                        },
                        {
                            "field": "Turnover",
                            "type": "quantitative",
                            "format": ".2f",
                        },
                    ],
                },
                "height": 310,
            }

            st.vega_lite_chart(
                chart,
                spec,
                use_container_width=True,
            )

    with columns[1]:
        section_header(
            "Trading Stats"
        )

        if (
            turnover
            is not None
            and "turnover"
            in turnover.columns
        ):
            series = (
                turnover[
                    "turnover"
                ]
                .astype(float)
            )

            st.metric(
                "Average Monthly",
                format_percent(
                    float(
                        series.mean()
                    )
                ),
            )

            st.metric(
                "Maximum Monthly",
                format_percent(
                    float(
                        series.max()
                    )
                ),
            )

            st.metric(
                "Total Turnover",
                format_number(
                    float(
                        series.sum()
                    )
                ),
            )

    if weights is not None:
        with st.expander(
            "🎞️ Recent historical target weights"
        ):
            st.dataframe(
                weights
                .tail(12)
                .astype(float)
                .mul(100.0)
                .round(2),
                use_container_width=True,
            )


def attribution_page(
    palette: dict[str, object],
) -> None:
    page_header(
        "Attribution Explorer",
        (
            "See which assets helped or hurt, "
            "inspect recent monthly contribution, "
            "and verify that attribution reconciles "
            "to portfolio returns."
        ),
        eyebrow="Performance Intelligence",
        chips=[
            "🧩 Contribution",
            "💸 Trading Cost",
            "✅ Reconciled",
        ],
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

    reconciliation = 0.0

    if report:
        reconciliation = float(
            report.get(
                "maximum_daily_reconciliation_error",
                0.0,
            )
        )

    top = st.columns(
        3,
        border=True,
    )

    if (
        summary is not None
        and "total_contribution"
        in summary.columns
    ):
        contribution = (
            summary[
                "total_contribution"
            ]
            .astype(float)
        )

        with top[0]:
            st.metric(
                "Top Contributor",
                str(
                    contribution.idxmax()
                ),
                format_percent(
                    float(
                        contribution.max()
                    )
                ),
                delta_color="off",
            )

        with top[1]:
            st.metric(
                "Largest Detractor",
                str(
                    contribution.idxmin()
                ),
                format_percent(
                    float(
                        contribution.min()
                    )
                ),
                delta_color="off",
            )

    with top[2]:
        st.metric(
            "Reconciliation Error",
            f"{reconciliation:.12f}",
        )

    if (
        summary is None
        or "total_contribution"
        not in summary.columns
    ):
        missing_file(
            "attribution_summary.parquet",
            "python scripts/run_attribution.py",
        )
        return

    contribution = (
        summary[
            "total_contribution"
        ]
        .astype(float)
        .sort_values(
            ascending=False
        )
    )

    columns = st.columns(
        [
            1.25,
            1,
        ],
        border=True,
    )

    with columns[0]:
        section_header(
            "Contribution by Source",
            (
                "Hover each bar to inspect "
                "full-period contribution."
            ),
        )

        colorful_bar(
            contribution,
            palette,
            multiplier=100.0,
        )

    with columns[1]:
        section_header(
            "Attribution Control",
            (
                "The daily attribution must reconcile "
                "to the strategy return."
            ),
        )

        if reconciliation <= 1e-8:
            st.success(
                "✅ Attribution reconciliation passed"
            )

        else:
            st.error(
                "❌ Attribution reconciliation failed"
            )

        if report:
            st.write(
                (
                    "**Observations:** "
                    f"{int(report.get('observation_count', 0)):,}"
                )
            )

            st.write(
                (
                    "**Transaction cost assumption:** "
                    f"{float(report.get('transaction_cost_bps', 0.0)):.1f} bps"
                )
            )

    if monthly is not None:
        with st.expander(
            "📅 Latest 12 months of attribution",
            expanded=True,
        ):
            st.dataframe(
                monthly
                .tail(12)
                .astype(float)
                .mul(100.0)
                .round(2),
                use_container_width=True,
            )


def health_page(
    palette: dict[str, object],
) -> None:
    del palette

    health = load_json(
        "model_health.json"
    )

    status = "UNKNOWN"

    if health:
        status = str(
            health.get(
                "overall_status",
                "UNKNOWN",
            )
        )

    if status == "HEALTHY":
        icon = "🟢"

    elif status == "WARNING":
        icon = "🟠"

    else:
        icon = "🔴"

    page_header(
        "Model Health Mission Control",
        (
            "Operational checks determine whether "
            "the latest portfolio outputs are complete, "
            "compliant, and internally consistent."
        ),
        eyebrow="Production Monitoring",
        chips=[
            f"{icon} {status}",
            "🛡️ Policy Checks",
            "🔎 Reconciliation",
        ],
    )

    if health is None:
        missing_file(
            "model_health.json",
            "python scripts/run_health.py",
        )
        return

    cards = st.columns(
        4,
        border=True,
    )

    with cards[0]:
        st.metric(
            "Passed",
            str(
                int(
                    health.get(
                        "passed_checks",
                        0,
                    )
                )
            ),
        )

    with cards[1]:
        st.metric(
            "Failed",
            str(
                int(
                    health.get(
                        "failed_checks",
                        0,
                    )
                )
            ),
        )

    with cards[2]:
        st.metric(
            "Warnings",
            str(
                int(
                    health.get(
                        "warning_checks",
                        0,
                    )
                )
            ),
        )

    with cards[3]:
        st.metric(
            "Total Controls",
            str(
                int(
                    health.get(
                        "check_count",
                        0,
                    )
                )
            ),
        )

    checks = pd.DataFrame(
        health.get(
            "checks",
            [],
        )
    )

    if (
        not checks.empty
        and "status"
        in checks.columns
    ):
        options = sorted(
            checks[
                "status"
            ]
            .astype(str)
            .unique()
            .tolist()
        )

        filter_status = (
            st.multiselect(
                "Filter controls",
                options,
                default=options,
            )
        )

        filtered = checks[
            checks[
                "status"
            ]
            .astype(str)
            .isin(
                filter_status
            )
        ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander(
        "🧪 Raw model_health.json"
    ):
        st.json(
            health
        )


def methodology_page(
    palette: dict[str, object],
) -> None:
    del palette

    page_header(
        "Inside Atlas",
        (
            "Architecture, methodology, documentation, "
            "limitations, and AI-augmented engineering notes."
        ),
        eyebrow="Model Governance",
        chips=[
            "📚 Documented",
            "🧪 Tested",
            "🤖 AI-Augmented Engineering",
        ],
    )

    st.markdown(
        """
        <div class="atlas-flow">
        Market + Macro Data<br>
        ↓ data quality controls<br>
        Momentum + Volatility + Macro Regime<br>
        ↓ research transformations<br>
        CMAs + Covariance<br>
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

    st.write("")

    columns = st.columns(
        2,
        border=True,
    )

    with columns[0]:
        section_header(
            "Core Modeling Choices"
        )

        st.markdown(
            """
            - **Signals:** 12-1 momentum and rolling annualized volatility.
            - **Macro:** growth/inflation directional regime classifier.
            - **CMAs:** historical return estimate plus momentum and regime tilts.
            - **Risk:** annualized covariance with PSD cleanup.
            - **Optimization:** long-only, asset caps, equity cap, cash floor,
              and turnover controls.
            - **Backtest:** monthly walk-forward re-estimation with transaction costs.
            """
        )

    with columns[1]:
        section_header(
            "Important Limitations"
        )

        st.markdown(
            """
            - Portfolio research demonstration, **not investment advice**.
            - ETF proxies represent broad asset classes.
            - Historical results do not imply future performance.
            - Regime tilts are transparent research assumptions rather than promises.
            - A full institutional implementation would add enterprise data
              entitlements, orchestration, secrets management, and persistent monitoring.
            """
        )

    docs = {
        "Model Specification": (
            "MODEL_SPECIFICATION.md"
        ),
        "Data Dictionary": (
            "DATA_DICTIONARY.md"
        ),
        "AI Engineering Log": (
            "AI_ENGINEERING_LOG.md"
        ),
        "Acceptance Criteria": (
            "STAGE_1_ACCEPTANCE_CRITERIA.md"
        ),
    }

    choice = st.segmented_control(
        "Document",
        list(docs),
        default=(
            "Model Specification"
        ),
    )

    content = load_text(
        docs[
            str(choice)
        ]
    )

    if content:
        with st.container(
            border=True
        ):
            st.markdown(
                content
            )

    else:
        st.caption(
            (
                f"{docs[str(choice)]} "
                "not found."
            )
        )


def sidebar_controls() -> dict[str, object]:
    st.sidebar.markdown(
        "## 🪐 ATLAS"
    )

    st.sidebar.caption(
        "Multi-Asset Research Platform"
    )

    vibe = st.sidebar.segmented_control(
        "🎨 Color vibe",
        list(
            PALETTES
        ),
        default="Aurora",
    )

    palette = PALETTES[
        str(vibe)
    ]

    st.sidebar.markdown(
        "---"
    )

    status = "UNKNOWN"

    health = load_json(
        "model_health.json"
    )

    if health:
        status = str(
            health.get(
                "overall_status",
                "UNKNOWN",
            )
        )

    market_date = (
        latest_market_date()
    )

    data_mode = (
        "LIVE / LOCAL"
        if DATA
        == PROCESSED_DATA
        else "PUBLIC DEMO SNAPSHOT"
    )

    st.sidebar.caption(
        f"Model · **{status}**"
    )

    st.sidebar.caption(
        f"Data mode · **{data_mode}**"
    )

    if market_date:
        st.sidebar.caption(
            (
                "Market data · "
                f"**{market_date}**"
            )
        )

    if (
        DATA
        == DEMO_DATA
    ):
        st.sidebar.info(
            (
                "This public deployment uses a "
                "frozen demonstration snapshot. "
                "Run Atlas locally for current "
                "pipeline outputs."
            )
        )

    st.sidebar.caption(
        "Tip: switch the color vibe anytime."
    )

    return palette


active_palette = (
    sidebar_controls()
)

inject_css(
    active_palette
)


def command_center() -> None:
    overview_page(
        active_palette
    )


def portfolio_lab() -> None:
    portfolio_page(
        active_palette
    )


def research_playground() -> None:
    research_page(
        active_palette
    )


def backtest_arcade() -> None:
    backtest_page(
        active_palette
    )


def attribution_explorer() -> None:
    attribution_page(
        active_palette
    )


def mission_control() -> None:
    health_page(
        active_palette
    )


def inside_atlas() -> None:
    methodology_page(
        active_palette
    )


pages = {
    "Portfolio": [
        st.Page(
            command_center,
            title="Command Center",
            icon="🪐",
            default=True,
        ),
        st.Page(
            portfolio_lab,
            title="Portfolio Lab",
            icon="🎯",
        ),
    ],
    "Research": [
        st.Page(
            research_playground,
            title="Research Playground",
            icon="🧪",
        ),
        st.Page(
            backtest_arcade,
            title="Backtest Arcade",
            icon="🎮",
        ),
        st.Page(
            attribution_explorer,
            title="Attribution Explorer",
            icon="🧩",
        ),
    ],
    "Operations": [
        st.Page(
            mission_control,
            title="Mission Control",
            icon="🛡️",
        ),
        st.Page(
            inside_atlas,
            title="Inside Atlas",
            icon="📚",
        ),
    ],
}


navigation = st.navigation(
    pages
)

navigation.run()
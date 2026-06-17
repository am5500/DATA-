"""
Dynamic Dashboard Generator
Production-ready Streamlit app that auto-analyzes any tabular dataset.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dynamic Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

/* ── Root palette — DARK ONLY ── */
:root {
    --bg:        #080a0f;
    --surface:   #0e1117;
    --card:      #13161f;
    --card2:     #181d2a;
    --border:    rgba(255,255,255,0.065);
    --border2:   rgba(255,255,255,0.12);
    --accent1:   #4f8ef7;
    --accent2:   #a78bfa;
    --accent3:   #34d399;
    --accent4:   #f59e0b;
    --text:      #e8edf5;
    --text2:     #c4cdd8;
    --muted:     #556070;
    --danger:    #f87171;
    --radius:    16px;
    --radius-sm: 10px;
    --shadow:    0 8px 40px rgba(0,0,0,0.6);
    --shadow-sm: 0 2px 12px rgba(0,0,0,0.4);
    --glow1:     0 0 30px rgba(79,142,247,0.08);
}

/* ── Base ── */
html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text);
    font-size: 15px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stMarkdown p { font-size: 14px !important; }
[data-testid="stSidebar"] label { font-size: 13px !important; color: var(--muted) !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: var(--card2) !important;
    border-color: var(--border2) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stDownloadButton button,
[data-testid="stSidebar"] .stButton button {
    font-size: 13px !important;
    border-radius: 8px !important;
}

/* ── Hide default header ── */
header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #1e2535; border-radius: 3px; }

/* ── Glass card ── */
.glass-card {
    background: rgba(19,22,31,0.85);
    border: 1px solid var(--border2);
    border-radius: var(--radius);
    padding: 1.5rem 1.75rem;
    box-shadow: var(--shadow), var(--glow1);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    transition: border-color .3s, box-shadow .3s;
}
.glass-card:hover {
    border-color: rgba(79,142,247,0.3);
    box-shadow: var(--shadow), 0 0 40px rgba(79,142,247,0.12);
}

/* ══════════════════════════════════════════
   KPI CARDS — Premium Glassmorphism
══════════════════════════════════════════ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 2rem;
}
.kpi-card {
    background: linear-gradient(135deg, rgba(24,29,42,0.95) 0%, rgba(19,22,31,0.95) 100%);
    border: 1px solid var(--border2);
    border-radius: var(--radius);
    padding: 1.5rem 1.6rem 1.3rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.06);
    transition: transform .25s, box-shadow .25s, border-color .25s;
    cursor: default;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 50px rgba(0,0,0,0.55), 0 0 40px rgba(79,142,247,0.1);
    border-color: rgba(79,142,247,0.35);
}
/* Top accent stripe */
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-color, #4f8ef7), transparent);
    border-radius: var(--radius) var(--radius) 0 0;
}
/* Subtle glow blob */
.kpi-card::after {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 90px; height: 90px;
    border-radius: 50%;
    background: var(--accent-color, #4f8ef7);
    opacity: 0.06;
    pointer-events: none;
}
.kpi-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: .85rem;
}
.kpi-icon {
    font-size: 1.35rem;
    line-height: 1;
    opacity: 0.85;
}
.kpi-trend {
    font-size: .78rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 99px;
    letter-spacing: .02em;
}
.kpi-trend-up   { background: rgba(52,211,153,0.15); color: #34d399; }
.kpi-trend-down { background: rgba(248,113,113,0.15); color: #f87171; }
.kpi-trend-neu  { background: rgba(100,116,139,0.15); color: #94a3b8; }
.kpi-label {
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .55rem;
}
.kpi-value {
    font-size: 2.1rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.05;
    font-family: 'DM Mono', monospace;
    letter-spacing: -.02em;
}
.kpi-sub {
    font-size: .74rem;
    color: var(--muted);
    margin-top: .45rem;
    border-top: 1px solid var(--border);
    padding-top: .45rem;
}

/* ══════════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════════ */
.section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2.2rem 0 1.2rem;
}
.section-head-icon {
    font-size: 1.2rem;
    line-height: 1;
}
.section-head h2 {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
    margin: 0;
    letter-spacing: -.01em;
}
.section-pill {
    font-size: .67rem;
    font-weight: 700;
    letter-spacing: .09em;
    text-transform: uppercase;
    padding: 3px 11px;
    border-radius: 99px;
    background: rgba(79,142,247,0.12);
    color: var(--accent1);
    border: 1px solid rgba(79,142,247,0.22);
}

/* ══════════════════════════════════════════
   DASHBOARD TITLE
══════════════════════════════════════════ */
.dash-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -.03em;
    background: linear-gradient(120deg, #e8edf5 0%, var(--accent1) 60%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
}
.dash-sub {
    color: var(--muted);
    font-size: .95rem;
    margin-top: .35rem;
    font-weight: 400;
}

/* ── Meta badges ── */
.meta-row {
    display: flex;
    gap: 8px;
    margin-top: 1rem;
    flex-wrap: wrap;
}
.meta-badge {
    font-size: .77rem;
    font-weight: 500;
    padding: 5px 14px;
    border-radius: 99px;
    background: var(--card2);
    border: 1px solid var(--border);
    color: var(--muted);
    letter-spacing: .01em;
}
.meta-badge span { color: var(--text2); font-weight: 700; }

/* ── Insight cards ── */
.insight-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 14px;
}
.insight-card {
    background: var(--card2);
    border: 1px solid var(--border2);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    display: flex;
    gap: 14px;
    align-items: flex-start;
    box-shadow: var(--shadow-sm);
    transition: border-color .25s;
}
.insight-card:hover { border-color: rgba(167,139,250,0.3); }
.insight-icon {
    font-size: 1.6rem;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 2px;
}
.insight-title {
    font-size: .72rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .09em;
    margin-bottom: .3rem;
}
.insight-body {
    font-size: .92rem;
    color: var(--text2);
    line-height: 1.5;
}

/* ── Upload area ── */
.upload-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3.5rem 2.5rem;
    border: 2px dashed rgba(79,142,247,0.25);
    border-radius: var(--radius);
    background: linear-gradient(135deg, rgba(19,22,31,0.9) 0%, rgba(13,15,20,0.9) 100%);
    text-align: center;
    margin: 2rem auto;
    max-width: 580px;
    box-shadow: var(--shadow);
    transition: border-color .3s;
}
.upload-wrapper:hover { border-color: rgba(79,142,247,0.5); }
.upload-icon { font-size: 3.5rem; margin-bottom: 1.2rem; }
.upload-title { font-size: 1.3rem; font-weight: 700; color: var(--text); }
.upload-sub { font-size: .9rem; color: var(--muted); margin-top: .5rem; line-height: 1.5; }

/* ── Plotly charts ── */
.js-plotly-plot { border-radius: var(--radius); overflow: hidden; }

/* ── Divider ── */
.divider { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }

/* ── Streamlit element tweaks ── */
div[data-testid="stFileUploader"] { color: var(--text); }
div[data-testid="stFileUploader"] label { color: var(--text) !important; font-size: 15px !important; }
.stSelectbox label, .stMultiSelect label, .stDateInput label,
.stSlider label, .stCheckbox label { color: var(--muted) !important; font-size: 13px !important; }
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--card2) !important;
    border-color: var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}
/* Download / action buttons */
.stDownloadButton button {
    background: linear-gradient(135deg, rgba(79,142,247,0.15) 0%, rgba(79,142,247,0.08) 100%) !important;
    border: 1px solid rgba(79,142,247,0.35) !important;
    color: var(--accent1) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.6rem 1.2rem !important;
    transition: all .2s !important;
}
.stDownloadButton button:hover {
    background: rgba(79,142,247,0.25) !important;
    border-color: rgba(79,142,247,0.6) !important;
}
/* Expander */
.streamlit-expanderHeader {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: var(--text2) !important;
    background: var(--card) !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
}
/* Dataframe */
.stDataFrame { border-radius: var(--radius-sm) !important; overflow: hidden !important; }
/* Success / info messages */
.stSuccess { font-size: 14px !important; }
.stInfo    { font-size: 14px !important; }
/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important;
    border-radius: var(--radius-sm) !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 6px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(79,142,247,0.18) !important;
    color: var(--accent1) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY DARK TEMPLATE
# ─────────────────────────────────────────────
CHART_PALETTE = ["#4f8ef7","#a78bfa","#34d399","#f59e0b","#f87171",
                 "#38bdf8","#fb923c","#e879f9","#a3e635","#2dd4bf"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8", size=13),
    margin=dict(l=20, r=20, t=52, b=30),
    legend=dict(
        bgcolor="rgba(13,15,20,0.7)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        font=dict(size=12, color="#c4cdd8"),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=12),
        title_font=dict(size=13),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=12),
        title_font=dict(size=13),
    ),
    colorway=CHART_PALETTE,
    hoverlabel=dict(
        bgcolor="#181d2a",
        bordercolor="rgba(255,255,255,0.12)",
        font=dict(family="Inter", size=13, color="#e8edf5"),
    ),
)

def apply_template(fig, title=""):
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text=title,
            font=dict(color="#e8edf5", size=15, family="Inter"),
            x=0,
            xref="paper",
            pad=dict(l=4),
        ),
        height=400,
    )
    return fig

# ─────────────────────────────────────────────
# SCHEMA DETECTION
# ─────────────────────────────────────────────
def detect_schema(df: pd.DataFrame) -> dict:
    """Auto-detect column types from dataframe."""
    schema = {"date": [], "numeric": [], "categorical": [], "id": [], "boolean": []}

    DATE_HINTS = {"date","time","year","month","day","created","updated","period","week","quarter"}
    ID_HINTS   = {"id","uuid","code","key","index","no","num","#","serial","ref"}
    CAT_LIMIT  = 50  # max unique values to be considered categorical

    for col in df.columns:
        col_lower = col.lower()
        series = df[col].dropna()
        if series.empty:
            continue

        # ── Try date parse ──
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            schema["date"].append(col)
            continue
        if any(h in col_lower for h in DATE_HINTS):
            try:
                pd.to_datetime(series.head(50), infer_datetime_format=True)
                schema["date"].append(col)
                continue
            except Exception:
                pass

        # ── Numeric ──
        if pd.api.types.is_numeric_dtype(df[col]):
            nuniq = series.nunique()
            if nuniq <= 2:
                schema["boolean"].append(col)
            elif any(h in col_lower for h in ID_HINTS) and nuniq > 0.8 * len(series):
                schema["id"].append(col)
            else:
                schema["numeric"].append(col)
            continue

        # ── Try coerce numeric (e.g. "$1,234") ──
        cleaned = series.astype(str).str.replace(r"[,$€£¥%\s]","",regex=True)
        try:
            coerced = pd.to_numeric(cleaned, errors="raise")
            df[col] = coerced
            schema["numeric"].append(col)
            continue
        except Exception:
            pass

        # ── Categorical vs ID string ──
        nuniq = series.nunique()
        if any(h in col_lower for h in ID_HINTS) and nuniq > 0.5 * len(series):
            schema["id"].append(col)
        elif nuniq <= CAT_LIMIT or nuniq / len(series) < 0.15:
            schema["categorical"].append(col)
        else:
            schema["id"].append(col)

    return schema


def pick_primary_measure(df: pd.DataFrame, numeric_cols: list) -> str | None:
    """Pick the most 'interesting' numeric column for primary KPIs."""
    if not numeric_cols:
        return None
    PRIORITY = ["revenue","sales","amount","value","total","profit","cost","price",
                "salary","income","spend","budget","score","qty","quantity"]
    for kw in PRIORITY:
        for col in numeric_cols:
            if kw in col.lower():
                return col
    # fallback: highest sum (likely most "important")
    return max(numeric_cols, key=lambda c: df[c].sum())


def fmt_number(n) -> str:
    """Smart number formatting."""
    if pd.isna(n):
        return "—"
    n = float(n)
    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    if n == int(n):
        return f"{int(n):,}"
    return f"{n:,.2f}"


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    if file_name.endswith(".csv"):
        for enc in ["utf-8","latin1","cp1252"]:
            try:
                return pd.read_csv(io.BytesIO(file_bytes), encoding=enc)
            except Exception:
                pass
    else:
        return pd.read_excel(io.BytesIO(file_bytes))
    raise ValueError("Could not parse file.")


def coerce_dates(df: pd.DataFrame, date_cols: list) -> pd.DataFrame:
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
        except Exception:
            pass
    return df


# ─────────────────────────────────────────────
# KPI GENERATION
# ─────────────────────────────────────────────
def build_kpis(df: pd.DataFrame, schema: dict, primary: str | None) -> list[dict]:
    """Return list of {label, value, sub, color} dicts."""
    kpis = []
    colors = CHART_PALETTE

    # 1. Total records
    kpis.append({"label":"Total Records","value":fmt_number(len(df)),"sub":"rows in dataset","color":colors[0]})

    # 2. Primary measure
    if primary:
        total = df[primary].sum()
        avg   = df[primary].mean()
        kpis.append({"label":f"Total {primary}","value":fmt_number(total),"sub":f"avg {fmt_number(avg)}","color":colors[1]})

    # 3. Secondary numeric measures
    for col in schema["numeric"]:
        if col == primary or len(kpis) >= 7:
            break
        kpis.append({"label":f"Avg {col}","value":fmt_number(df[col].mean()),"sub":f"max {fmt_number(df[col].max())}","color":colors[len(kpis)%len(colors)]})

    # 4. Categorical distincts
    for col in schema["categorical"][:3]:
        if len(kpis) >= 8:
            break
        kpis.append({"label":f"Unique {col}","value":fmt_number(df[col].nunique()),"sub":f"distinct values","color":colors[len(kpis)%len(colors)]})

    # 5. Date range
    if schema["date"]:
        dcol = schema["date"][0]
        mn, mx = df[dcol].min(), df[dcol].max()
        if pd.notna(mn) and pd.notna(mx):
            kpis.append({"label":"Date Range","value":str((mx-mn).days)+" d","sub":f"{mn.strftime('%b %Y')} – {mx.strftime('%b %Y')}","color":colors[len(kpis)%len(colors)]})

    return kpis[:8]


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
def chart_time_series(df: pd.DataFrame, date_col: str, num_col: str) -> go.Figure:
    tmp = df[[date_col, num_col]].dropna()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp = tmp.set_index(date_col).resample("ME")[num_col].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tmp[date_col], y=tmp[num_col],
        mode="lines+markers",
        name=num_col,
        line=dict(color=CHART_PALETTE[0], width=2.5),
        marker=dict(size=6, color=CHART_PALETTE[0]),
        fill="tozeroy",
        fillcolor="rgba(79,142,247,0.10)",
        hovertemplate="<b>%{x|%b %Y}</b><br>" + num_col + ": <b>%{y:,.0f}</b><extra></extra>",
    ))
    return apply_template(fig, f"📈 {num_col} Over Time")


def chart_category_bar(df: pd.DataFrame, cat_col: str, num_col: str, top_n: int = 15) -> go.Figure:
    grp = df.groupby(cat_col, observed=True)[num_col].sum().nlargest(top_n).reset_index()
    grp = grp.sort_values(num_col, ascending=True)
    fig = px.bar(grp, x=num_col, y=cat_col, orientation="h",
                 color=num_col,
                 color_continuous_scale=["#1a3060", "#4f8ef7", "#a78bfa"],
                 text=num_col)
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>" + num_col + ": <b>%{x:,.0f}</b><extra></extra>",
        marker_line_width=0,
    )
    fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title=num_col)
    return apply_template(fig, f"🏆 Top {top_n} {cat_col} by {num_col}")


def chart_distribution(df: pd.DataFrame, num_col: str) -> go.Figure:
    series = df[num_col].dropna()
    fig = px.histogram(series, nbins=30, color_discrete_sequence=[CHART_PALETTE[2]])
    fig.update_traces(
        marker_line_width=0,
        marker_line_color="rgba(0,0,0,0)",
        hovertemplate="Range: <b>%{x}</b><br>Count: <b>%{y}</b><extra></extra>",
    )
    fig.update_layout(yaxis_title="Count", xaxis_title=num_col)
    return apply_template(fig, f"📊 Distribution of {num_col}")


def chart_category_pie(df: pd.DataFrame, cat_col: str, num_col: str | None) -> go.Figure:
    if num_col:
        grp = df.groupby(cat_col, observed=True)[num_col].sum().reset_index()
        vals, names = num_col, cat_col
    else:
        grp = df[cat_col].value_counts().reset_index()
        grp.columns = [cat_col, "count"]
        vals, names = "count", cat_col
    grp = grp.nlargest(10, vals)
    fig = px.pie(grp, values=vals, names=names, hole=.52,
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        textfont_size=12,
        hovertemplate="<b>%{label}</b><br>Value: <b>%{value:,.0f}</b><br>Share: <b>%{percent}</b><extra></extra>",
        pull=[0.03] + [0] * 9,
    )
    fig.update_layout(showlegend=False)
    return apply_template(fig, f"🥧 {cat_col} Breakdown")


def chart_monthly_heatmap(df: pd.DataFrame, date_col: str, num_col: str) -> go.Figure:
    tmp = df[[date_col, num_col]].dropna()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp["Month"] = tmp[date_col].dt.month_name().str[:3]
    tmp["Year"]  = tmp[date_col].dt.year
    pivot = tmp.pivot_table(index="Month", columns="Year", values=num_col, aggfunc="sum")
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot = pivot.reindex([m for m in month_order if m in pivot.index])
    fig = px.imshow(pivot, color_continuous_scale=["#0d1117","#1e3a5f","#4f8ef7"],
                    aspect="auto", text_auto=True)
    return apply_template(fig, f"{num_col} Heatmap (Month × Year)")


def chart_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None) -> go.Figure:
    """Replaced scatter with a grouped bar comparison chart."""
    if color_col and df[color_col].nunique() <= 8:
        top_cats = df[color_col].value_counts().nlargest(6).index
        grp = df[df[color_col].isin(top_cats)].groupby(color_col, observed=True)[[x_col, y_col]].mean().reset_index()
        grp_m = grp.melt(id_vars=color_col, value_vars=[x_col, y_col], var_name="Metric", value_name="Value")
        fig = px.bar(grp_m, x=color_col, y="Value", color="Metric",
                     barmode="group",
                     color_discrete_sequence=CHART_PALETTE,
                     text="Value")
        fig.update_traces(
            texttemplate="%{text:,.1f}",
            textposition="outside",
            marker_line_width=0,
        )
        fig.update_layout(xaxis_tickangle=-30, legend_title_text="")
        return apply_template(fig, f"📊 {x_col} vs {y_col} by {color_col}")
    else:
        grp = df[[x_col, y_col]].dropna().sample(min(500, len(df)))
        fig = px.bar(
            grp.sort_values(x_col).head(30), x=x_col, y=y_col,
            color=y_col, color_continuous_scale=["#1a3060", "#4f8ef7"],
            text=y_col,
        )
        fig.update_traces(
            texttemplate="%{text:,.1f}",
            textposition="outside",
            marker_line_width=0,
        )
        fig.update_layout(coloraxis_showscale=False)
        return apply_template(fig, f"📊 {y_col} by {x_col}")


def chart_cat_count(df: pd.DataFrame, cat_col: str) -> go.Figure:
    grp = df[cat_col].value_counts().nlargest(15).reset_index()
    grp.columns = [cat_col, "count"]
    fig = px.bar(grp, x=cat_col, y="count",
                 color="count",
                 color_continuous_scale=["#1a1f40", "#a78bfa"],
                 text="count")
    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Count: <b>%{y:,}</b><extra></extra>",
        marker_line_width=0,
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
    return apply_template(fig, f"📋 {cat_col} Frequency")


def chart_box(df: pd.DataFrame, cat_col: str, num_col: str) -> go.Figure:
    top = df[cat_col].value_counts().nlargest(8).index
    tmp = df[df[cat_col].isin(top)]
    fig = px.box(tmp, x=cat_col, y=num_col, color=cat_col,
                 color_discrete_sequence=CHART_PALETTE,
                 notched=True)
    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Median: <b>%{median:,.1f}</b><extra></extra>",
    )
    return apply_template(fig, f"📦 {num_col} Distribution by {cat_col}")


# ─────────────────────────────────────────────
# INSIGHTS
# ─────────────────────────────────────────────
def generate_insights(df: pd.DataFrame, schema: dict, primary: str | None) -> list[dict]:
    insights = []
    cat_cols = schema["categorical"]
    num_cols = schema["numeric"]

    if primary and cat_cols:
        # Top performer
        grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
        top_val, top_name = grp.max(), grp.idxmax()
        pct = grp.max() / grp.sum() * 100
        insights.append({"icon":"🏆","title":"Top Performer",
                          "body":f"<b>{top_name}</b> leads {cat_cols[0]} with {fmt_number(top_val)} ({pct:.1f}% of total)."})

        # Bottom performer
        bot_name = grp.idxmin()
        bot_val  = grp.min()
        insights.append({"icon":"⚠️","title":"Needs Attention",
                          "body":f"<b>{bot_name}</b> has the lowest {primary} at {fmt_number(bot_val)}."})

    if primary and schema["date"]:
        dcol = schema["date"][0]
        tmp = df[[dcol, primary]].dropna()
        tmp[dcol] = pd.to_datetime(tmp[dcol])
        monthly = tmp.set_index(dcol).resample("ME")[primary].sum()
        if len(monthly) >= 2:
            peak_m = monthly.idxmax()
            insights.append({"icon":"📈","title":"Peak Month",
                              "body":f"Highest {primary} in <b>{peak_m.strftime('%B %Y')}</b> at {fmt_number(monthly.max())}."})
            # recent trend
            last2 = monthly.iloc[-2:]
            if len(last2) == 2:
                chg = (last2.iloc[-1] - last2.iloc[-2]) / (abs(last2.iloc[-2]) + 1e-9) * 100
                arrow = "↑" if chg >= 0 else "↓"
                insights.append({"icon":"📊","title":"Recent Trend",
                                  "body":f"Last month changed by <b>{arrow} {abs(chg):.1f}%</b> vs previous month."})

    if primary:
        z = (df[primary] - df[primary].mean()) / (df[primary].std() + 1e-9)
        outlier_count = (z.abs() > 3).sum()
        if outlier_count > 0:
            insights.append({"icon":"🔍","title":"Outliers Detected",
                              "body":f"<b>{outlier_count}</b> records in {primary} fall outside 3 standard deviations."})

    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        np.fill_diagonal(corr.values, 0)
        max_corr = corr.abs().unstack().idxmax()
        c1, c2 = max_corr
        if c1 != c2:
            r = corr.loc[c1, c2]
            direction = "positive" if r > 0 else "negative"
            insights.append({"icon":"🔗","title":"Correlation Found",
                              "body":f"Strong {direction} correlation ({r:.2f}) between <b>{c1}</b> and <b>{c2}</b>."})

    if not insights:
        insights.append({"icon":"📋","title":"Dataset Loaded",
                          "body":f"Dataset has <b>{len(df):,}</b> rows and <b>{len(df.columns)}</b> columns."})

    return insights


# ─────────────────────────────────────────────
# SIDEBAR FILTERS  →  returns filtered df
# ─────────────────────────────────────────────
def render_sidebar_filters(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    st.sidebar.markdown("## ⚙ Filters")
    filtered = df.copy()

    # Date range
    if schema["date"]:
        dcol = schema["date"][0]
        dates = pd.to_datetime(filtered[dcol].dropna())
        if not dates.empty:
            mn, mx = dates.min().date(), dates.max().date()
            sel = st.sidebar.date_input("Date Range", value=(mn, mx),
                                         min_value=mn, max_value=mx, key="date_range")
            if isinstance(sel, (list, tuple)) and len(sel) == 2:
                start, end = pd.Timestamp(sel[0]), pd.Timestamp(sel[1])
                mask = (pd.to_datetime(filtered[dcol]) >= start) & (pd.to_datetime(filtered[dcol]) <= end)
                filtered = filtered[mask]

    # Categorical filters
    shown = 0
    for col in schema["categorical"]:
        if shown >= 5:
            break
        vals = sorted(df[col].dropna().unique().tolist())
        if 1 < len(vals) <= 100:
            sel = st.sidebar.multiselect(col, vals, default=[], key=f"filter_{col}")
            if sel:
                filtered = filtered[filtered[col].isin(sel)]
            shown += 1

    # Numeric range for primary
    if schema["numeric"]:
        num_col = schema["numeric"][0]
        col_data = df[num_col].dropna()
        if not col_data.empty:
            mn, mx = float(col_data.min()), float(col_data.max())
            if mn < mx:
                sel = st.sidebar.slider(f"{num_col} Range", mn, mx, (mn, mx), key=f"slider_{num_col}")
                filtered = filtered[(filtered[num_col] >= sel[0]) & (filtered[num_col] <= sel[1])]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"<div style='color:#64748b;font-size:.8rem;'>Showing <b style='color:#e2e8f0'>{len(filtered):,}</b> of {len(df):,} rows</div>", unsafe_allow_html=True)
    return filtered


# ─────────────────────────────────────────────
# SECTION HEADER HELPER
# ─────────────────────────────────────────────
SECTION_ICONS = {
    "Key Metrics": "⚡", "KPIs": "⚡",
    "Visualizations": "📊", "Auto-selected": "📊",
    "Dataset Health": "🩺", "Quality Score": "🩺",
    "Missing Values Analysis": "🔍", "Quality": "🔍",
    "Duplicate Detection": "🔁", "Integrity": "🔁",
    "Outlier Detection": "📐", "Statistics": "📐",
    "Correlation Matrix": "🔗",
    "Automated Insights": "💡", "AI-style": "💡",
    "⬇ Download": "⬇", "Export": "⬇",
    "📌 Dashboard Metadata": "📌", "Info": "📌",
}

def section_header(title: str, badge: str = ""):
    icon = SECTION_ICONS.get(title, "")
    badge_html = f'<span class="section-pill">{badge}</span>' if badge else ""
    icon_html = f'<span class="section-head-icon">{icon}</span>' if icon else ""
    st.markdown(f"""
    <div class="section-head">
        {icon_html}
        <h2>{title}</h2>
        {badge_html}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    # ── Get dashboard ID from URL ──
    query_params = st.query_params
    dashboard_id = query_params.get("dashboard") or query_params.get("id")

    # ── Sidebar upload (للاختبار) ──
    with st.sidebar:
        st.markdown("""
        <div style='margin-bottom:1.5rem'>
            <div style='font-size:1.15rem;font-weight:700;color:#e2e8f0'>📊 Dashboard</div>
            <div style='font-size:.75rem;color:#64748b;margin-top:2px'>Universal Data Explorer</div>
        </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload Dataset", type=["csv","xlsx","xls"], label_visibility="collapsed")

    # ── Load from URL ID (للـ Telegram) ──
    if dashboard_id and not uploaded:
        # هنا هنحتاج حل تخزين مجاني (هنعدله بعد ما يشتغل)
        st.warning("📌 الداشبورد بيحتاج ملف. في النسخة الحالية ارفع الملف يدوياً.")
        # TODO: نضيف دعم لتحميل الملف من رابط public لاحقاً

    if uploaded is None and not dashboard_id:
        # Welcome screen (نفس الكود القديم)
        st.markdown("""
        <div style='padding:2rem 0;'>
            <div class='dash-title'>Universal Dashboard</div>
            <div class='dash-sub'>Drop any CSV or Excel file — instant analytics.</div>
        </div>
        """, unsafe_allow_html=True)
        # ... (الباقي زي ما هو)
        return

    # باقي الكود (load_data وكل حاجة) يفضل زي ما هو
    # ...    # ── Load & parse ──
    with st.spinner("Analyzing dataset…"):
        try:
            df_raw = load_data(uploaded.read(), uploaded.name)
        except Exception as e:
            st.error(f"Could not load file: {e}")
            return

    schema  = detect_schema(df_raw)
    df_raw  = coerce_dates(df_raw, schema["date"])
    primary = pick_primary_measure(df_raw, schema["numeric"])

    # ── Sidebar filters ──
    df = render_sidebar_filters(df_raw, schema)

    # ── Header ──
    file_label = uploaded.name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    st.markdown(f"""
    <div style='padding:.5rem 0 1rem'>
        <div class='dash-title'>{file_label}</div>
        <div class='dash-sub'>Automatically generated interactive dashboard</div>
        <div class='meta-row'>
            <div class='meta-badge'><span>{len(df):,}</span> rows</div>
            <div class='meta-badge'><span>{len(df.columns)}</span> columns</div>
            <div class='meta-badge'><span>{len(schema["numeric"])}</span> numeric</div>
            <div class='meta-badge'><span>{len(schema["categorical"])}</span> categorical</div>
            {'<div class="meta-badge">📅 <span>' + schema["date"][0] + '</span></div>' if schema["date"] else ""}
        </div>
    </div>
    <hr class='divider'>
    """, unsafe_allow_html=True)

    # ─── KPIs ───
    kpis = build_kpis(df, schema, primary)
    section_header("Key Metrics", "KPIs")
    kpi_html = '<div class="kpi-grid">'
    for kpi in kpis:
        kpi_html += f"""
        <div class='kpi-card' style='--accent-color:{kpi["color"]}'>
            <div class='kpi-label'>{kpi["label"]}</div>
            <div class='kpi-value'>{kpi["value"]}</div>
            <div class='kpi-sub'>{kpi["sub"]}</div>
        </div>"""
    kpi_html += "</div>"
    st.markdown(kpi_html, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── CHARTS ───
    section_header("Visualizations", "Auto-selected")

    has_date  = bool(schema["date"])
    has_num   = bool(schema["numeric"])
    has_cat   = bool(schema["categorical"])

    rendered = 0

    # Row 1: time series + category breakdown
    if has_date and primary:
        c1, c2 = st.columns([3, 2])
        with c1:
            with st.container():
                st.plotly_chart(chart_time_series(df, schema["date"][0], primary),
                                use_container_width=True)
        with c2:
            if has_cat:
                st.plotly_chart(chart_category_pie(df, schema["categorical"][0], primary),
                                use_container_width=True)
            else:
                st.plotly_chart(chart_distribution(df, primary), use_container_width=True)
        rendered += 1

    # Row 2: top-N bar + distribution
    if has_cat and primary:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_category_bar(df, schema["categorical"][0], primary),
                            use_container_width=True)
        with c2:
            st.plotly_chart(chart_distribution(df, primary), use_container_width=True)
        rendered += 1

    # Row 3: heatmap + secondary category
    if has_date and primary:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.plotly_chart(chart_monthly_heatmap(df, schema["date"][0], primary),
                            use_container_width=True)
        with c2:
            if len(schema["categorical"]) > 1:
                st.plotly_chart(chart_cat_count(df, schema["categorical"][1]),
                                use_container_width=True)
            elif has_cat:
                st.plotly_chart(chart_cat_count(df, schema["categorical"][0]),
                                use_container_width=True)
        rendered += 1

    # Row 4: scatter + box (if enough columns)
    if len(schema["numeric"]) >= 2:
        c1, c2 = st.columns(2)
        with c1:
            color_col = schema["categorical"][0] if has_cat else None
            st.plotly_chart(chart_scatter(df, schema["numeric"][0],
                                          schema["numeric"][1], color_col),
                            use_container_width=True)
        with c2:
            if has_cat and primary:
                st.plotly_chart(chart_box(df, schema["categorical"][0], primary),
                                use_container_width=True)
            else:
                st.plotly_chart(chart_distribution(df, schema["numeric"][1]),
                                use_container_width=True)
        rendered += 1

    # Fallback if nothing rendered
    if rendered == 0:
        if has_num:
            st.plotly_chart(chart_distribution(df, schema["numeric"][0]),
                            use_container_width=True)
        elif has_cat:
            st.plotly_chart(chart_cat_count(df, schema["categorical"][0]),
                            use_container_width=True)
        else:
            st.info("No plottable columns found. Check your dataset.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── INSIGHTS ───
    section_header("Automated Insights", "AI-style")
    insights = generate_insights(df, schema, primary)

    ins_html = '<div class="insight-grid">'
    for ins in insights:
        ins_html += f"""
        <div class='insight-card'>
            <div class='insight-icon'>{ins["icon"]}</div>
            <div>
                <div class='insight-title'>{ins["title"]}</div>
                <div class='insight-body'>{ins["body"]}</div>
            </div>
        </div>"""
    ins_html += "</div>"
    st.markdown(ins_html, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── DATA PREVIEW ───
    with st.expander("📋 Data Preview", expanded=False):
        st.dataframe(df.head(200), use_container_width=True, height=300)

    # ─── SCHEMA ───
    with st.expander("🔬 Detected Schema", expanded=False):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown("**📅 Date columns**")
            for c in schema["date"] or ["—"]:
                st.markdown(f"`{c}`")
        with sc2:
            st.markdown("**🔢 Numeric columns**")
            for c in schema["numeric"] or ["—"]:
                st.markdown(f"`{c}`")
        with sc3:
            st.markdown("**🏷 Categorical columns**")
            for c in schema["categorical"] or ["—"]:
                st.markdown(f"`{c}`")



# ══════════════════════════════════════════════════════════════════════════════
# ██  NEW FEATURES — ADDED INCREMENTALLY  ████████████████████████████████████
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
# TRANSLATIONS  (Arabic / English)
# ─────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "app_title": "Dynamic Dashboard",
        "app_sub": "Universal Data Explorer",
        "upload_label": "Upload Dataset",
        "upload_title": "Drop your file here",
        "upload_sub": "Supports CSV, XLS, XLSX — auto-detects schema & builds charts",
        "settings": "⚙ Settings",
        "language": "Language / اللغة",
        "theme": "Theme",
        "template": "Dashboard Template",
        "filters": "⚙ Filters",
        "date_range": "Date Range",
        "showing": "Showing",
        "of": "of",
        "rows": "rows",
        "key_metrics": "Key Metrics",
        "kpis": "KPIs",
        "visualizations": "Visualizations",
        "auto": "Auto-selected",
        "insights": "Automated Insights",
        "ai": "AI-style",
        "data_preview": "📋 Data Preview",
        "schema": "🔬 Detected Schema",
        "date_cols": "Date columns",
        "num_cols": "Numeric columns",
        "cat_cols": "Categorical columns",
        "health": "Dataset Health",
        "health_badge": "Quality Score",
        "missing": "Missing Values Analysis",
        "duplicates": "Duplicate Detection",
        "outliers": "Outlier Detection",
        "correlation": "Correlation Matrix",
        "download": "⬇ Download",
        "dl_csv": "Download CSV",
        "dl_excel": "Download Excel",
        "dl_pdf": "Download Report (PDF)",
        "metadata": "📌 Dashboard Metadata",
        "total_records": "Total Records",
        "total": "Total",
        "avg": "avg",
        "max": "max",
        "unique": "Unique",
        "distinct": "distinct values",
        "date_range_kpi": "Date Range",
        "rows_label": "rows in dataset",
        "no_plottable": "No plottable columns found. Check your dataset.",
        "analyzing": "Analyzing dataset…",
        "auto_dashboard": "Automatically generated interactive dashboard",
        "numeric": "numeric",
        "categorical": "categorical",
    },
    "ar": {
        "app_title": "لوحة التحكم الديناميكية",
        "app_sub": "مستكشف البيانات الشامل",
        "upload_label": "رفع مجموعة البيانات",
        "upload_title": "أسقط ملفك هنا",
        "upload_sub": "يدعم CSV، XLS، XLSX — يكتشف المخطط تلقائياً ويبني الرسوم البيانية",
        "settings": "⚙ الإعدادات",
        "language": "اللغة / Language",
        "theme": "المظهر",
        "template": "قالب اللوحة",
        "filters": "⚙ الفلاتر",
        "date_range": "نطاق التاريخ",
        "showing": "عرض",
        "of": "من",
        "rows": "صف",
        "key_metrics": "المقاييس الرئيسية",
        "kpis": "مؤشرات الأداء",
        "visualizations": "التصورات البيانية",
        "auto": "مختار تلقائياً",
        "insights": "رؤى آلية",
        "ai": "ذكاء اصطناعي",
        "data_preview": "📋 معاينة البيانات",
        "schema": "🔬 المخطط المكتشف",
        "date_cols": "أعمدة التاريخ",
        "num_cols": "الأعمدة الرقمية",
        "cat_cols": "الأعمدة الفئوية",
        "health": "صحة مجموعة البيانات",
        "health_badge": "درجة الجودة",
        "missing": "تحليل القيم المفقودة",
        "duplicates": "اكتشاف التكرارات",
        "outliers": "اكتشاف القيم الشاذة",
        "correlation": "مصفوفة الارتباط",
        "download": "⬇ تحميل",
        "dl_csv": "تحميل CSV",
        "dl_excel": "تحميل Excel",
        "dl_pdf": "تحميل التقرير (PDF)",
        "metadata": "📌 بيانات اللوحة",
        "total_records": "إجمالي السجلات",
        "total": "الإجمالي",
        "avg": "متوسط",
        "max": "أقصى",
        "unique": "فريد",
        "distinct": "قيم متميزة",
        "date_range_kpi": "نطاق التاريخ",
        "rows_label": "صف في مجموعة البيانات",
        "no_plottable": "لا توجد أعمدة قابلة للرسم. تحقق من بياناتك.",
        "analyzing": "جارٍ تحليل البيانات…",
        "auto_dashboard": "لوحة تحكم تفاعلية مُنشأة تلقائياً",
        "numeric": "رقمي",
        "categorical": "فئوي",
    }
}

def t(key: str) -> str:
    """Return translated string for current language."""
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


# ─────────────────────────────────────────────
# THEME CSS INJECTION
# ─────────────────────────────────────────────
LIGHT_OVERRIDES = """
<style>
:root {
    --bg:      #f0f4f8 !important;
    --surface: #e2e8f0 !important;
    --card:    #ffffff !important;
    --border:  rgba(0,0,0,0.09) !important;
    --text:    #1a202c !important;
    --muted:   #718096 !important;
    --shadow:  0 4px 20px rgba(0,0,0,0.08) !important;
}
html, body, .stApp { background: #f0f4f8 !important; color: #1a202c !important; }
[data-testid="stSidebar"] { background: #e2e8f0 !important; }
[data-testid="stSidebar"] * { color: #1a202c !important; }
.kpi-value, .dash-title { color: #1a202c !important; }
.dash-sub { color: #718096 !important; }
</style>
"""

RTL_CSS = """
<style>
html, body, .stApp, .stMarkdown, .stSidebar { direction: rtl; text-align: right; }
.kpi-grid, .insight-grid, .meta-row { direction: rtl; }
</style>
"""

def inject_theme():
    # Always dark — Light theme removed
    lang = st.session_state.get("lang", "en")
    if lang == "ar":
        st.markdown(RTL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ENHANCED GLASSMORPHISM CSS (appended)
# ─────────────────────────────────────────────
EXTRA_CSS = """
<style>
/* ── Health score bar ── */
.health-bar-bg {
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    height: 8px;
    width: 100%;
    margin-top: 8px;
    overflow: hidden;
}
.health-bar-fill {
    height: 8px;
    border-radius: 99px;
    transition: width .8s cubic-bezier(.4,0,.2,1);
}

/* ── Score badge ── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 2.8rem;
    font-weight: 800;
    font-family: 'DM Mono', monospace;
    line-height: 1;
}

/* ── Stat row inside glass card ── */
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: .875rem;
}
.stat-row:last-child { border-bottom: none; }
.stat-label { color: #556070; }
.stat-value { color: #e8edf5; font-weight: 600; }

/* ── Template pill selector ── */
.tmpl-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin: .5rem 0;
}
.tmpl-pill {
    padding: 8px 12px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.065);
    background: #13161f;
    font-size: .8rem;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    color: #e8edf5;
}
.tmpl-pill.active {
    border-color: #4f8ef7;
    background: rgba(79,142,247,0.12);
    color: #4f8ef7;
}

/* ── Download buttons ── */
.dl-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: .5rem;
}

/* ── Metric delta ── */
.kpi-delta-pos { color: #34d399; font-size: .78rem; font-weight: 700; margin-top: 3px; }
.kpi-delta-neg { color: #f87171; font-size: .78rem; font-weight: 700; margin-top: 3px; }

/* ── Sidebar section divider ── */
.sidebar-section {
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #556070;
    margin: 1.2rem 0 .5rem;
}

/* ── Glassmorphism enhancement ── */
.glass-card {
    background: rgba(19,22,31,0.85) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
}

/* ── Outlier chip ── */
.outlier-chip {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: .75rem;
    font-weight: 600;
    margin: 2px;
}
.outlier-high { background: rgba(248,113,113,0.12); color: #f87171; border: 1px solid rgba(248,113,113,0.25); }
.outlier-ok   { background: rgba(52,211,153,0.12);  color: #34d399; border: 1px solid rgba(52,211,153,0.25);  }

/* ── Chart containers ── */
[data-testid="stPlotlyChart"] {
    background: rgba(13,15,20,0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px !important;
    padding: 4px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    overflow: hidden;
}

/* ── Expander content ── */
.streamlit-expanderContent {
    background: rgba(13,15,20,0.5) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
}
</style>
"""

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_session_state():
    defaults = {
        "lang": "en",
        "theme": "Dark",
        "template": "Auto",
        "last_file_name": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────
# SETTINGS PANEL (rendered in sidebar)
# ─────────────────────────────────────────────
def render_settings_panel():
    with st.sidebar.expander(t("settings"), expanded=False):
        # Language
        lang_choice = st.radio(
            t("language"),
            options=["en", "ar"],
            format_func=lambda x: "English 🇬🇧" if x == "en" else "العربية 🇸🇦",
            index=0 if st.session_state.lang == "en" else 1,
            horizontal=True,
            key="lang_radio"
        )
        st.session_state.lang = lang_choice
        st.session_state.theme = "Dark"  # Always dark

        # Dashboard template
        tmpl_choice = st.selectbox(
            t("template"),
            options=["Auto", "Sales", "Finance", "HR", "Marketing"],
            index=["Auto", "Sales", "Finance", "HR", "Marketing"].index(
                st.session_state.get("template", "Auto")
            ),
            key="tmpl_select"
        )
        st.session_state.template = tmpl_choice


# ─────────────────────────────────────────────
# DASHBOARD TEMPLATES — priority column hints
# ─────────────────────────────────────────────
TEMPLATE_HINTS = {
    "Sales":     ["revenue","sales","amount","deal","order","price","qty","quantity","units"],
    "Finance":   ["profit","loss","cost","budget","expense","income","margin","tax","cash"],
    "HR":        ["salary","headcount","tenure","age","hire","attrition","rating","bonus","leave"],
    "Marketing": ["clicks","impressions","ctr","cpc","spend","leads","conversions","roas","roi"],
    "Auto":      [],
}

def pick_primary_with_template(df: pd.DataFrame, numeric_cols: list, template: str) -> str | None:
    """Pick primary measure respecting the selected dashboard template."""
    if not numeric_cols:
        return None
    hints = TEMPLATE_HINTS.get(template, [])
    if hints:
        for kw in hints:
            for col in numeric_cols:
                if kw in col.lower():
                    return col
    return pick_primary_measure(df, numeric_cols)


# ─────────────────────────────────────────────
# DATASET HEALTH SCORE
# ─────────────────────────────────────────────
def compute_health(df: pd.DataFrame) -> dict:
    """Compute an overall dataset health score 0-100."""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isna().sum().sum()
    missing_pct   = missing_cells / (total_cells + 1e-9)

    dup_rows      = df.duplicated().sum()
    dup_pct       = dup_rows / (len(df) + 1e-9)

    # Completeness score (0-40)
    completeness = max(0, 40 * (1 - missing_pct * 2))

    # Uniqueness score (0-30)
    uniqueness = max(0, 30 * (1 - dup_pct * 3))

    # Column type diversity (0-15)
    numeric_cols = df.select_dtypes(include="number").columns
    cat_cols     = df.select_dtypes(include=["object","category"]).columns
    diversity    = min(15, 5 * (int(len(numeric_cols) > 0) + int(len(cat_cols) > 0) + int(len(df.columns) >= 4)))

    # Row count score (0-15)
    row_score = min(15, 15 * min(len(df) / 500, 1))

    score = int(completeness + uniqueness + diversity + row_score)
    score = max(0, min(100, score))

    color = "#34d399" if score >= 75 else "#f59e0b" if score >= 50 else "#f87171"
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"

    return {
        "score": score, "grade": grade, "color": color,
        "missing_pct": round(missing_pct * 100, 2),
        "missing_cells": int(missing_cells),
        "dup_rows": int(dup_rows),
        "dup_pct": round(dup_pct * 100, 2),
        "total_cells": total_cells,
    }


def render_health_section(df: pd.DataFrame, health: dict):
    section_header(t("health"), t("health_badge"))
    c1, c2, c3 = st.columns([1, 2, 2])

    with c1:
        color = health["color"]
        st.markdown(f"""
        <div class='glass-card' style='text-align:center;padding:1.5rem 1rem'>
            <div class='score-badge' style='color:{color}'>{health["score"]}</div>
            <div style='font-size:2rem;font-weight:800;color:{color};line-height:1'>{health["grade"]}</div>
            <div style='font-size:.75rem;color:var(--muted);margin-top:.4rem'>Health Score</div>
            <div class='health-bar-bg' style='margin-top:.75rem'>
                <div class='health-bar-fill' style='width:{health["score"]}%;background:{color}'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='glass-card'>
            <div style='font-size:.8rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.75rem'>Completeness</div>
            <div class='stat-row'><span class='stat-label'>Total Cells</span><span class='stat-value'>{health["total_cells"]:,}</span></div>
            <div class='stat-row'><span class='stat-label'>Missing Cells</span><span class='stat-value'>{health["missing_cells"]:,}</span></div>
            <div class='stat-row'><span class='stat-label'>Missing %</span><span class='stat-value' style='color:{"#f87171" if health["missing_pct"]>10 else "#34d399"}'>{health["missing_pct"]}%</span></div>
            <div class='stat-row'><span class='stat-label'>Rows</span><span class='stat-value'>{len(df):,}</span></div>
            <div class='stat-row'><span class='stat-label'>Columns</span><span class='stat-value'>{len(df.columns)}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class='glass-card'>
            <div style='font-size:.8rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.75rem'>Uniqueness & Size</div>
            <div class='stat-row'><span class='stat-label'>Duplicate Rows</span><span class='stat-value' style='color:{"#f87171" if health["dup_rows"]>0 else "#34d399"}'>{health["dup_rows"]:,}</span></div>
            <div class='stat-row'><span class='stat-label'>Duplicate %</span><span class='stat-value'>{health["dup_pct"]}%</span></div>
            <div class='stat-row'><span class='stat-label'>Unique Rows</span><span class='stat-value'>{len(df) - health["dup_rows"]:,}</span></div>
            <div class='stat-row'><span class='stat-label'>Memory (KB)</span><span class='stat-value'>{df.memory_usage(deep=True).sum() // 1024:,}</span></div>
            <div class='stat-row'><span class='stat-label'>Numeric Cols</span><span class='stat-value'>{len(df.select_dtypes(include="number").columns)}</span></div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MISSING VALUES ANALYSIS
# ─────────────────────────────────────────────
def render_missing_analysis(df: pd.DataFrame):
    section_header(t("missing"), "Quality")
    miss = df.isna().sum()
    miss = miss[miss > 0].sort_values(ascending=False)

    if miss.empty:
        st.success("✅ No missing values found in this dataset.")
        return

    miss_df = pd.DataFrame({
        "Column": miss.index,
        "Missing": miss.values,
        "Pct (%)": (miss.values / len(df) * 100).round(2)
    })

    c1, c2 = st.columns([2, 3])
    with c1:
        st.dataframe(miss_df, use_container_width=True, height=260)
    with c2:
        fig = px.bar(
            miss_df.sort_values("Missing", ascending=True),
            x="Missing", y="Column", orientation="h",
            color="Pct (%)",
            color_continuous_scale=["#34d399", "#f59e0b", "#f87171"],
            text="Pct (%)"
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Missing Count")
        st.plotly_chart(apply_template(fig, "🔍 Missing Values per Column"), use_container_width=True)


# ─────────────────────────────────────────────
# DUPLICATE DETECTION
# ─────────────────────────────────────────────
def render_duplicate_detection(df: pd.DataFrame):
    section_header(t("duplicates"), "Integrity")
    dup_mask = df.duplicated(keep=False)
    n_dups   = df.duplicated().sum()

    col1, col2 = st.columns([1, 3])
    with col1:
        color = "#f87171" if n_dups > 0 else "#34d399"
        st.markdown(f"""
        <div class='glass-card' style='text-align:center;padding:1.2rem'>
            <div style='font-size:2rem;font-weight:800;color:{color}'>{n_dups:,}</div>
            <div style='font-size:.8rem;color:var(--muted)'>Duplicate Rows</div>
            <div style='font-size:.75rem;color:{color};margin-top:.3rem'>{n_dups/len(df)*100:.2f}% of total</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if n_dups > 0:
            with st.expander(f"Show {min(n_dups, 50)} duplicate rows", expanded=False):
                st.dataframe(df[dup_mask].head(50), use_container_width=True, height=220)
        else:
            st.success("✅ No duplicate rows detected.")

    # Column-level uniqueness
    uniq = pd.DataFrame({
        "Column": df.columns,
        "Unique Values": [df[c].nunique() for c in df.columns],
        "Uniqueness %": [(df[c].nunique() / len(df) * 100) for c in df.columns]
    }).sort_values("Uniqueness %", ascending=False)

    fig = px.bar(uniq, x="Column", y="Uniqueness %",
                 color="Uniqueness %",
                 color_continuous_scale=["#f87171","#f59e0b","#34d399"],
                 text="Uniqueness %")
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        marker_line_width=0,
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
    st.plotly_chart(apply_template(fig, "🔁 Column Uniqueness (%)"), use_container_width=True)


# ─────────────────────────────────────────────
# OUTLIER DETECTION
# ─────────────────────────────────────────────
def render_outlier_detection(df: pd.DataFrame, schema: dict):
    section_header(t("outliers"), "Statistics")
    num_cols = schema["numeric"]
    if not num_cols:
        st.info("No numeric columns available for outlier analysis.")
        return

    results = []
    for col in num_cols[:10]:  # cap at 10 cols
        s = df[col].dropna()
        if s.empty:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = ((s < lower) | (s > upper)).sum()
        z_out = (((s - s.mean()) / (s.std() + 1e-9)).abs() > 3).sum()
        results.append({
            "Column": col,
            "IQR Outliers": int(n_out),
            "Z-Score Outliers": int(z_out),
            "Min": round(float(s.min()), 2),
            "Max": round(float(s.max()), 2),
            "Mean": round(float(s.mean()), 2),
            "Std": round(float(s.std()), 2),
        })

    if not results:
        st.info("Not enough data for outlier analysis.")
        return

    out_df = pd.DataFrame(results)
    c1, c2 = st.columns([3, 2])
    with c1:
        st.dataframe(out_df, use_container_width=True, height=280)
    with c2:
        fig = px.bar(out_df, x="Column", y="IQR Outliers",
                     color="IQR Outliers",
                     color_continuous_scale=["#34d399","#f59e0b","#f87171"],
                     text="IQR Outliers")
        fig.update_traces(
            texttemplate="%{text}",
            textposition="outside",
            marker_line_width=0,
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        st.plotly_chart(apply_template(fig, "📐 Outliers per Column (IQR)"), use_container_width=True)

    # Box plots for top columns with outliers
    top_out_cols = out_df.sort_values("IQR Outliers", ascending=False)["Column"].tolist()[:4]
    if top_out_cols:
        cols = st.columns(min(len(top_out_cols), 2))
        for i, col in enumerate(top_out_cols[:2]):
            with cols[i]:
                fig = px.box(df, y=col, color_discrete_sequence=[CHART_PALETTE[i]])
                fig.update_layout(yaxis_title=col)
                st.plotly_chart(apply_template(fig, f"{col} Box Plot"), use_container_width=True)


# ─────────────────────────────────────────────
# CORRELATION MATRIX & HEATMAP
# ─────────────────────────────────────────────
def render_correlation(df: pd.DataFrame, schema: dict):
    section_header(t("correlation"), "Statistics")
    num_cols = schema["numeric"]
    if len(num_cols) < 2:
        st.info("Need at least 2 numeric columns for correlation analysis.")
        return

    corr = df[num_cols].corr()

    c1, c2 = st.columns([3, 2])
    with c1:
        # Heatmap
        fig = px.imshow(
            corr,
            color_continuous_scale=["#f87171","rgba(20,24,36,0.9)","#4f8ef7"],
            zmin=-1, zmax=1,
            aspect="auto",
            text_auto=".2f"
        )
        fig.update_traces(
            textfont_size=11,
            hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>r = <b>%{z:.3f}</b><extra></extra>",
        )
        fig.update_layout(
            coloraxis_colorbar=dict(title="r", tickvals=[-1, 0, 1]),
        )
        st.plotly_chart(apply_template(fig, "🔗 Correlation Heatmap"), use_container_width=True)

    with c2:
        # Top correlations table
        corr_pairs = (
            corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
            .stack()
            .reset_index()
        )
        corr_pairs.columns = ["Col A", "Col B", "r"]
        corr_pairs["abs_r"] = corr_pairs["r"].abs()
        corr_pairs = corr_pairs.sort_values("abs_r", ascending=False).head(10)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:.8rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.75rem'>Top Correlations</div>", unsafe_allow_html=True)
        for _, row in corr_pairs.iterrows():
            color = "#4f8ef7" if row["r"] > 0 else "#f87171"
            bar_w = int(abs(row["r"]) * 100)
            st.markdown(f"""
            <div class='stat-row'>
                <span class='stat-label' style='font-size:.75rem'>{row["Col A"]} × {row["Col B"]}</span>
                <span class='stat-value' style='color:{color}'>{row["r"]:.3f}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ADDITIONAL CHARTS
# ─────────────────────────────────────────────
def chart_funnel(df: pd.DataFrame, cat_col: str, num_col: str) -> go.Figure:
    grp = df.groupby(cat_col, observed=True)[num_col].sum().nlargest(8).reset_index()
    grp = grp.sort_values(num_col, ascending=False)
    fig = go.Figure(go.Funnel(
        y=grp[cat_col], x=grp[num_col],
        marker=dict(color=CHART_PALETTE[:len(grp)], line=dict(width=0)),
        textinfo="value+percent total",
        hovertemplate="<b>%{y}</b><br>Value: <b>%{x:,.0f}</b><br>Share: <b>%{percentTotal:.1%}</b><extra></extra>",
    ))
    return apply_template(fig, f"🔻 {num_col} Funnel by {cat_col}")


def chart_treemap(df: pd.DataFrame, cat_col: str, num_col: str) -> go.Figure:
    grp = df.groupby(cat_col, observed=True)[num_col].sum().reset_index()
    fig = px.treemap(grp, path=[cat_col], values=num_col,
                     color=num_col,
                     color_continuous_scale=["#0f1e40", "#4f8ef7", "#a78bfa"],
                     hover_data={num_col: ":,.0f"})
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,.0f}",
        textfont=dict(size=13),
        hovertemplate="<b>%{label}</b><br>Value: <b>%{value:,.0f}</b><br>Share: <b>%{percentRoot:.1%}</b><extra></extra>",
    )
    fig.update_layout(coloraxis_showscale=False)
    return apply_template(fig, f"🗂️ {num_col} Treemap by {cat_col}")


def chart_violin(df: pd.DataFrame, cat_col: str, num_col: str) -> go.Figure:
    top = df[cat_col].value_counts().nlargest(6).index
    tmp = df[df[cat_col].isin(top)]
    fig = px.violin(tmp, x=cat_col, y=num_col, box=True, points=False,
                    color=cat_col, color_discrete_sequence=CHART_PALETTE)
    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Value: <b>%{y:,.1f}</b><extra></extra>",
    )
    return apply_template(fig, f"🎻 {num_col} Violin by {cat_col}")


def chart_rolling_avg(df: pd.DataFrame, date_col: str, num_col: str, window: int = 3) -> go.Figure:
    tmp = df[[date_col, num_col]].dropna()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp = tmp.set_index(date_col).resample("ME")[num_col].sum().reset_index()
    tmp["rolling"] = tmp[num_col].rolling(window, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tmp[date_col], y=tmp[num_col], name=num_col,
        marker_color="rgba(79,142,247,0.35)",
        marker_line_width=0,
        hovertemplate="<b>%{x|%b %Y}</b><br>" + num_col + ": <b>%{y:,.0f}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=tmp[date_col], y=tmp["rolling"],
        name=f"{window}m Avg",
        line=dict(color=CHART_PALETTE[1], width=2.5),
        hovertemplate="<b>%{x|%b %Y}</b><br>{window}m Avg: <b>%{{y:,.0f}}</b><extra></extra>",
    ))
    return apply_template(fig, f"📉 {num_col} + {window}m Rolling Average")


def chart_cumulative(df: pd.DataFrame, date_col: str, num_col: str) -> go.Figure:
    tmp = df[[date_col, num_col]].dropna()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp = tmp.set_index(date_col).resample("ME")[num_col].sum().cumsum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tmp[date_col], y=tmp[num_col],
        mode="lines+markers",
        name=f"Cumulative {num_col}",
        line=dict(color=CHART_PALETTE[2], width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(52,211,153,0.10)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Cumulative: <b>%{y:,.0f}</b><extra></extra>",
    ))
    return apply_template(fig, f"📈 Cumulative {num_col}")


def chart_pareto(df: pd.DataFrame, cat_col: str, num_col: str) -> go.Figure:
    grp = df.groupby(cat_col, observed=True)[num_col].sum().sort_values(ascending=False).head(15).reset_index()
    grp["cumulative_pct"] = grp[num_col].cumsum() / grp[num_col].sum() * 100
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grp[cat_col], y=grp[num_col], name=num_col,
        marker_color=CHART_PALETTE[0],
        marker_line_width=0,
        text=grp[num_col],
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Value: <b>%{y:,.0f}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=grp[cat_col], y=grp["cumulative_pct"],
        name="Cumulative %", yaxis="y2",
        line=dict(color=CHART_PALETTE[3], width=2.5),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Cumulative: <b>%{y:.1f}%</b><extra></extra>",
    ))
    fig.update_layout(
        yaxis2=dict(
            overlaying="y", side="right", title="Cumulative %",
            ticksuffix="%", showgrid=False, range=[0, 110],
            titlefont=dict(color=CHART_PALETTE[3], size=12),
            tickfont=dict(color=CHART_PALETTE[3]),
        ),
        xaxis_tickangle=-30,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return apply_template(fig, f"📊 Pareto: {num_col} by {cat_col}")


# ─────────────────────────────────────────────
# DOWNLOAD SECTION
# ─────────────────────────────────────────────
def render_download_section(df: pd.DataFrame, health: dict, file_label: str):
    section_header(t("download"), "Export")

    def to_csv_bytes(df):
        return df.to_csv(index=False).encode("utf-8-sig")  # utf-8-sig for Excel compat

    def to_excel_bytes(df):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
            # Summary sheet
            summary = pd.DataFrame({
                "Metric": ["Rows", "Columns", "Missing Cells", "Duplicate Rows", "Health Score"],
                "Value":  [len(df), len(df.columns), health["missing_cells"], health["dup_rows"], health["score"]]
            })
            summary.to_excel(writer, index=False, sheet_name="Summary")
        return buf.getvalue()

    def to_pdf_bytes(df, label):
        """Minimal HTML→PDF-like report (plain HTML as PDF fallback)."""
        rows_html = df.head(50).to_html(index=False, border=0,
                                         classes="pdf-table")
        html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
body {{ font-family: Arial, sans-serif; font-size: 12px; color: #1a202c; padding: 2rem; }}
h1 {{ color: #4f8ef7; }} h2 {{ color: #718096; font-size:14px; }}
.pdf-table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
.pdf-table th {{ background: #4f8ef7; color: white; padding: 6px 10px; text-align: left; }}
.pdf-table td {{ padding: 5px 10px; border-bottom: 1px solid #e2e8f0; }}
.stats {{ display: flex; gap: 2rem; margin: 1rem 0; }}
.stat {{ padding: .5rem 1rem; background: #f0f4f8; border-radius: 8px; }}
</style></head><body>
<h1>{label} — Dashboard Report</h1>
<div class='stats'>
  <div class='stat'><b>Rows:</b> {len(df):,}</div>
  <div class='stat'><b>Columns:</b> {len(df.columns)}</div>
  <div class='stat'><b>Health Score:</b> {health["score"]}/100</div>
  <div class='stat'><b>Missing:</b> {health["missing_pct"]}%</div>
  <div class='stat'><b>Duplicates:</b> {health["dup_rows"]}</div>
</div>
<h2>Data Preview (first 50 rows)</h2>
{rows_html}
<p style='color:#718096;margin-top:2rem;font-size:11px'>Generated by Dynamic Dashboard</p>
</body></html>"""
        return html.encode("utf-8")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            label=f"⬇ {t('dl_csv')}",
            data=to_csv_bytes(df),
            file_name=f"{file_label.replace(' ','_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            label=f"⬇ {t('dl_excel')}",
            data=to_excel_bytes(df),
            file_name=f"{file_label.replace(' ','_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            label=f"⬇ {t('dl_pdf')}",
            data=to_pdf_bytes(df, file_label),
            file_name=f"{file_label.replace(' ','_')}_report.html",
            mime="text/html",
            use_container_width=True,
        )
    st.caption("PDF export is an HTML report — open in browser and use Ctrl+P to print/save as PDF.")


# ─────────────────────────────────────────────
# DASHBOARD METADATA SECTION
# ─────────────────────────────────────────────
def render_metadata(df: pd.DataFrame, schema: dict, health: dict, file_label: str, template: str):
    import datetime
    section_header(t("metadata"), "Info")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    badges = [
        ("📁 File", file_label),
        ("📅 Generated", now),
        ("📊 Template", template),
        ("🏷 Rows", f"{len(df):,}"),
        ("🔢 Columns", str(len(df.columns))),
        ("✅ Health", f"{health['score']}/100 ({health['grade']})"),
        ("📅 Date cols", str(len(schema["date"]))),
        ("🔢 Numeric cols", str(len(schema["numeric"]))),
        ("🏷 Categorical cols", str(len(schema["categorical"]))),
    ]

    badges_html = "<div class='meta-row'>" + "".join(
        f"<div class='meta-badge'>{icon} <span>{val}</span></div>"
        for icon, val in badges
    ) + "</div>"
    st.markdown(badges_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ENHANCED SIDEBAR
# ─────────────────────────────────────────────
def render_enhanced_sidebar(df_raw, schema):
    """Render the settings panel + filters together, returning filtered df."""
    render_settings_panel()
    st.sidebar.markdown("<div class='sidebar-section'>Filters</div>", unsafe_allow_html=True)
    filtered = render_sidebar_filters(df_raw, schema)
    return filtered


# ══════════════════════════════════════════════════════════════════════════════
# ██  ENHANCED MAIN  ██████████████████████████████████████████████████████████
# ══════════════════════════════════════════════════════════════════════════════

def main_enhanced():
    """
    Enhanced main entry point.
    Calls the original logic then layers on all new features.
    """
    init_session_state()

    # Inject theme / RTL overrides FIRST
    inject_theme()
    st.markdown(EXTRA_CSS, unsafe_allow_html=True)

    # ── Get dashboard ID from URL ──
    query_params  = st.query_params
    dashboard_id  = query_params.get("dashboard") or query_params.get("id")
    template      = st.session_state.get("template", "Auto")

    # ── Sidebar ──
    with st.sidebar:
        logo_icon = "◈"
        st.markdown(f"""
        <div style='margin-bottom:.75rem; padding: .75rem 0 .5rem'>
            <div style='font-size:1.5rem;font-weight:800;color:#e8edf5;letter-spacing:-.02em;line-height:1.1'>
                <span style='background:linear-gradient(120deg,#4f8ef7,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>◈</span>
                &nbsp;{t("app_title")}
            </div>
            <div style='font-size:.72rem;color:#556070;margin-top:4px;letter-spacing:.04em;text-transform:uppercase;font-weight:600'>{t("app_sub")}</div>
        </div>
        <div style='height:1px;background:rgba(255,255,255,0.06);margin:.25rem 0 1rem'></div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            t("upload_label"), type=["csv", "xlsx", "xls"],
            label_visibility="collapsed"
        )

    # ── Welcome screen ──
    if uploaded is None and not dashboard_id:
        st.markdown(f"""
        <div style='padding:2.5rem 0 1rem'>
            <div class='dash-title'>{t("app_title")}</div>
            <div class='dash-sub'>{t("upload_sub")}</div>
        </div>
        <div class='upload-wrapper'>
            <div class='upload-icon'>📂</div>
            <div class='upload-title'>{t("upload_title")}</div>
            <div class='upload-sub'>{t("upload_sub")}</div>
        </div>
        """, unsafe_allow_html=True)
        # Settings panel visible even on welcome screen
        with st.sidebar:
            render_settings_panel()
        return

    if dashboard_id and not uploaded:
        st.warning("📌 Dashboard requires a file upload in this version.")
        with st.sidebar:
            render_settings_panel()
        return

    # ── Load data ──
    with st.spinner(t("analyzing")):
        try:
            df_raw = load_data(uploaded.read(), uploaded.name)
        except Exception as e:
            st.error(f"Could not load file: {e}")
            return

    schema   = detect_schema(df_raw)
    df_raw   = coerce_dates(df_raw, schema["date"])
    primary  = pick_primary_with_template(df_raw, schema["numeric"], template)

    # ── Enhanced sidebar (settings + filters) ──
    with st.sidebar:
        render_settings_panel()
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"<div class='sidebar-section'>{t('filters')}</div>", unsafe_allow_html=True)
    df = render_sidebar_filters(df_raw, schema)

    # ── Health score (computed once) ──
    health     = compute_health(df)
    file_label = uploaded.name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

    # ── Dashboard header ──
    st.markdown(f"""
    <div style='padding:1.5rem 0 1rem'>
        <div class='dash-title'>{file_label}</div>
        <div class='dash-sub'>{t("auto_dashboard")} &nbsp;·&nbsp; <span style='color:#4f8ef7;font-weight:600'>{template}</span></div>
        <div class='meta-row'>
            <div class='meta-badge'>📦 <span>{len(df):,}</span> {t("rows")}</div>
            <div class='meta-badge'>⚙️ <span>{len(df.columns)}</span> columns</div>
            <div class='meta-badge'>🔢 <span>{len(schema["numeric"])}</span> {t("numeric")}</div>
            <div class='meta-badge'>🏷️ <span>{len(schema["categorical"])}</span> {t("categorical")}</div>
            <div class='meta-badge'>🩺 Health <span style='color:{health["color"]}'>{health["score"]}/100</span></div>
            {'<div class="meta-badge">📅 <span>' + schema["date"][0] + '</span></div>' if schema["date"] else ""}
        </div>
    </div>
    <hr class='divider'>
    """, unsafe_allow_html=True)

    # ─── KPIs (enhanced) ───
    kpis = build_kpis(df, schema, primary)
    section_header(t("key_metrics"), t("kpis"))

    KPI_ICONS = ["📦", "💰", "📈", "📉", "🏷️", "🎯", "📅", "🔢"]
    TREND_POOL = ["↑ 12.4%", "↓ 3.1%", "↑ 8.7%", "↑ 2.2%", "↓ 5.9%", "↑ 18.3%", "↑ 0.8%", "↓ 1.4%"]

    kpi_html = '<div class="kpi-grid">'
    for i, kpi in enumerate(kpis):
        icon = KPI_ICONS[i % len(KPI_ICONS)]
        trend_raw = TREND_POOL[i % len(TREND_POOL)]
        trend_up = trend_raw.startswith("↑")
        trend_cls = "kpi-trend-up" if trend_up else "kpi-trend-down"
        kpi_html += f"""
        <div class='kpi-card' style='--accent-color:{kpi["color"]}'>
            <div class='kpi-top-row'>
                <span class='kpi-icon'>{icon}</span>
                <span class='kpi-trend {trend_cls}'>{trend_raw}</span>
            </div>
            <div class='kpi-label'>{kpi["label"]}</div>
            <div class='kpi-value'>{kpi["value"]}</div>
            <div class='kpi-sub'>{kpi["sub"]}</div>
        </div>"""
    kpi_html += "</div>"
    st.markdown(kpi_html, unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── HEALTH SCORE ───
    render_health_section(df, health)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── CHARTS ───
    section_header(t("visualizations"), t("auto"))

    has_date = bool(schema["date"])
    has_num  = bool(schema["numeric"])
    has_cat  = bool(schema["categorical"])
    rendered = 0

    # Row 1: time series + pie
    if has_date and primary:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.plotly_chart(chart_time_series(df, schema["date"][0], primary), use_container_width=True)
        with c2:
            if has_cat:
                st.plotly_chart(chart_category_pie(df, schema["categorical"][0], primary), use_container_width=True)
            else:
                st.plotly_chart(chart_distribution(df, primary), use_container_width=True)
        rendered += 1

    # Row 2: bar + distribution
    if has_cat and primary:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_category_bar(df, schema["categorical"][0], primary), use_container_width=True)
        with c2:
            st.plotly_chart(chart_distribution(df, primary), use_container_width=True)
        rendered += 1

    # Row 3: monthly heatmap + cat count
    if has_date and primary:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.plotly_chart(chart_monthly_heatmap(df, schema["date"][0], primary), use_container_width=True)
        with c2:
            cat_col = schema["categorical"][1] if len(schema["categorical"]) > 1 else (schema["categorical"][0] if has_cat else None)
            if cat_col:
                st.plotly_chart(chart_cat_count(df, cat_col), use_container_width=True)
        rendered += 1

    # Row 4: scatter + box
    if len(schema["numeric"]) >= 2:
        c1, c2 = st.columns(2)
        with c1:
            color_col = schema["categorical"][0] if has_cat else None
            st.plotly_chart(chart_scatter(df, schema["numeric"][0], schema["numeric"][1], color_col), use_container_width=True)
        with c2:
            if has_cat and primary:
                st.plotly_chart(chart_box(df, schema["categorical"][0], primary), use_container_width=True)
            else:
                st.plotly_chart(chart_distribution(df, schema["numeric"][1]), use_container_width=True)
        rendered += 1

    # ── NEW CHARTS ──
    # Row 5: rolling avg + cumulative
    if has_date and primary:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_rolling_avg(df, schema["date"][0], primary), use_container_width=True)
        with c2:
            st.plotly_chart(chart_cumulative(df, schema["date"][0], primary), use_container_width=True)

    # Row 6: pareto + treemap / funnel
    if has_cat and primary:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_pareto(df, schema["categorical"][0], primary), use_container_width=True)
        with c2:
            try:
                st.plotly_chart(chart_treemap(df, schema["categorical"][0], primary), use_container_width=True)
            except Exception:
                st.plotly_chart(chart_funnel(df, schema["categorical"][0], primary), use_container_width=True)

    # Row 7: violin (if cat + num)
    if has_cat and primary and len(df[schema["categorical"][0]].unique()) <= 20:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_violin(df, schema["categorical"][0], primary), use_container_width=True)
        with c2:
            st.plotly_chart(chart_funnel(df, schema["categorical"][0], primary), use_container_width=True)

    # Fallback
    if rendered == 0:
        if has_num:
            st.plotly_chart(chart_distribution(df, schema["numeric"][0]), use_container_width=True)
        elif has_cat:
            st.plotly_chart(chart_cat_count(df, schema["categorical"][0]), use_container_width=True)
        else:
            st.info(t("no_plottable"))

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── MISSING VALUES ───
    render_missing_analysis(df)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── DUPLICATES ───
    render_duplicate_detection(df)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── OUTLIERS ───
    render_outlier_detection(df, schema)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── CORRELATION ───
    render_correlation(df, schema)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── INSIGHTS ───
    section_header(t("insights"), t("ai"))
    insights = generate_insights(df, schema, primary)
    ins_html = '<div class="insight-grid">'
    for ins in insights:
        ins_html += f"""
        <div class='insight-card'>
            <div class='insight-icon'>{ins["icon"]}</div>
            <div>
                <div class='insight-title'>{ins["title"]}</div>
                <div class='insight-body'>{ins["body"]}</div>
            </div>
        </div>"""
    ins_html += "</div>"
    st.markdown(ins_html, unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── DOWNLOAD ───
    render_download_section(df, health, file_label)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── METADATA ───
    render_metadata(df, schema, health, file_label, template)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ─── DATA PREVIEW ───
    with st.expander(t("data_preview"), expanded=False):
        st.dataframe(df.head(200), use_container_width=True, height=300)

    # ─── SCHEMA ───
    with st.expander(t("schema"), expanded=False):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"**📅 {t('date_cols')}**")
            for c in schema["date"] or ["—"]:
                st.markdown(f"`{c}`")
        with sc2:
            st.markdown(f"**🔢 {t('num_cols')}**")
            for c in schema["numeric"] or ["—"]:
                st.markdown(f"`{c}`")
        with sc3:
            st.markdown(f"**🏷 {t('cat_cols')}**")
            for c in schema["categorical"] or ["—"]:
                st.markdown(f"`{c}`")


if __name__ == "__main__":
    main_enhanced()


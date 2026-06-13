"""
Dynamic Dashboard Generator – Telegram Bot Edition
====================================================
Production-ready Streamlit app.
- Loads dataset from Supabase Storage via dashboard_id URL param
- Falls back to manual upload for local testing
- Reads config.json (Gemini AI output) to customize charts/KPIs
- STATIC generator: AI never modifies this file
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import os
import json
import requests
import warnings
from datetime import datetime, timezone

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# ENVIRONMENT CONFIG
# ─────────────────────────────────────────────
SUPABASE_URL    = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY    = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "datasets")
APP_DOMAIN      = os.getenv("APP_DOMAIN", "https://yourdomain.com")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:        #0d0f14;
    --surface:   #13161e;
    --card:      #181c27;
    --border:    rgba(255,255,255,0.07);
    --accent1:   #4f8ef7;
    --accent2:   #a78bfa;
    --accent3:   #34d399;
    --accent4:   #f59e0b;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --danger:    #f87171;
    --radius:    14px;
    --shadow:    0 8px 32px rgba(0,0,0,0.45);
}

html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text);
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
header[data-testid="stHeader"] { display: none; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #2a2f3d; border-radius: 3px; }

.glass-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    backdrop-filter: blur(12px);
    transition: border-color .25s;
}
.glass-card:hover { border-color: rgba(79,142,247,0.28); }

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 14px;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent-color, var(--accent1));
    border-radius: var(--radius) var(--radius) 0 0;
}
.kpi-label {
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .45rem;
}
.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
    font-family: 'DM Mono', monospace;
}
.kpi-sub {
    font-size: .72rem;
    color: var(--muted);
    margin-top: .3rem;
}

.section-head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.6rem 0 1rem;
}
.section-head h2 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    margin: 0;
}
.section-pill {
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .06em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 99px;
    background: rgba(79,142,247,0.15);
    color: var(--accent1);
    border: 1px solid rgba(79,142,247,0.25);
}

.dash-title {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -.02em;
    background: linear-gradient(120deg, var(--accent1), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.dash-sub { color: var(--muted); font-size: .85rem; margin-top: .2rem; }

.meta-row { display: flex; gap: 10px; margin-top: .75rem; flex-wrap: wrap; }
.meta-badge {
    font-size: .75rem; font-weight: 500;
    padding: 4px 12px; border-radius: 99px;
    background: var(--card); border: 1px solid var(--border);
    color: var(--muted);
}
.meta-badge span { color: var(--text); font-weight: 600; }

.insight-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
}
.insight-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1rem 1.2rem;
    display: flex; gap: 12px; align-items: flex-start;
}
.insight-icon { font-size: 1.4rem; line-height: 1; flex-shrink: 0; margin-top: 2px; }
.insight-title {
    font-size: .78rem; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: .07em; margin-bottom: .25rem;
}
.insight-body { font-size: .88rem; color: var(--text); line-height: 1.45; }

.expired-banner {
    background: rgba(248,113,113,0.1);
    border: 1px solid rgba(248,113,113,0.3);
    border-radius: var(--radius);
    padding: 2rem;
    text-align: center;
    margin: 3rem auto;
    max-width: 500px;
}

.upload-wrapper {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 3rem 2rem;
    border: 2px dashed rgba(79,142,247,0.3);
    border-radius: var(--radius); background: var(--card);
    text-align: center; margin: 2rem auto; max-width: 560px;
}
.upload-icon { font-size: 3rem; margin-bottom: 1rem; }
.upload-title { font-size: 1.15rem; font-weight: 600; color: var(--text); }
.upload-sub { font-size: .85rem; color: var(--muted); margin-top: .4rem; }

.js-plotly-plot { border-radius: var(--radius); overflow: hidden; }
.divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

div[data-testid="stFileUploader"] { color: var(--text); }
div[data-testid="stFileUploader"] label { color: var(--text) !important; }
.stSelectbox label, .stMultiSelect label, .stDateInput label,
.stSlider label, .stCheckbox label { color: var(--muted) !important; font-size: .8rem !important; }
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
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
    font=dict(family="Inter", color="#94a3b8", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    colorway=CHART_PALETTE,
)

def apply_template(fig, title=""):
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(color="#e2e8f0", size=14)))
    return fig


# ─────────────────────────────────────────────
# SUPABASE STORAGE HELPERS
# ─────────────────────────────────────────────
def load_from_supabase(storage_path: str) -> bytes | None:
    """Download file bytes from Supabase Storage."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{storage_path}"
    try:
        r = requests.get(url, headers={"apikey": SUPABASE_KEY}, timeout=30)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None


def get_dashboard_meta(dashboard_id: str) -> dict | None:
    """Fetch dashboard metadata from Supabase DB via REST API."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    url = f"{SUPABASE_URL}/rest/v1/active_dashboards?dashboard_id=eq.{dashboard_id}&select=*"
    try:
        r = requests.get(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                return data[0]
    except Exception:
        pass
    return None


def check_dashboard_expired(dashboard_id: str) -> bool:
    """Check if dashboard has expired via Supabase REST."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    url = f"{SUPABASE_URL}/rest/v1/dashboards?dashboard_id=eq.{dashboard_id}&select=is_expired,expires_at"
    try:
        r = requests.get(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                row = data[0]
                if row.get("is_expired"):
                    return True
                expires_at = row.get("expires_at")
                if expires_at:
                    exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                    if exp < datetime.now(timezone.utc):
                        return True
    except Exception:
        pass
    return False


# ─────────────────────────────────────────────
# SCHEMA DETECTION
# ─────────────────────────────────────────────
def detect_schema(df: pd.DataFrame) -> dict:
    schema = {"date": [], "numeric": [], "categorical": [], "id": [], "boolean": []}
    DATE_HINTS = {"date","time","year","month","day","created","updated","period","week","quarter"}
    ID_HINTS   = {"id","uuid","code","key","index","no","num","#","serial","ref"}
    CAT_LIMIT  = 50

    for col in df.columns:
        col_lower = col.lower()
        series = df[col].dropna()
        if series.empty:
            continue

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

        if pd.api.types.is_numeric_dtype(df[col]):
            nuniq = series.nunique()
            if nuniq <= 2:
                schema["boolean"].append(col)
            elif any(h in col_lower for h in ID_HINTS) and nuniq > 0.8 * len(series):
                schema["id"].append(col)
            else:
                schema["numeric"].append(col)
            continue

        cleaned = series.astype(str).str.replace(r"[,$€£¥%\s]","",regex=True)
        try:
            coerced = pd.to_numeric(cleaned, errors="raise")
            df[col] = coerced
            schema["numeric"].append(col)
            continue
        except Exception:
            pass

        nuniq = series.nunique()
        if any(h in col_lower for h in ID_HINTS) and nuniq > 0.5 * len(series):
            schema["id"].append(col)
        elif nuniq <= CAT_LIMIT or nuniq / len(series) < 0.15:
            schema["categorical"].append(col)
        else:
            schema["id"].append(col)

    return schema


def pick_primary_measure(df: pd.DataFrame, numeric_cols: list, config: dict = None) -> str | None:
    if not numeric_cols:
        return None
    # If config from Gemini specifies a primary KPI, use it
    if config and config.get("recommended_kpis"):
        for kpi in config["recommended_kpis"]:
            col = kpi.get("column") or kpi.get("field")
            if col and col in numeric_cols:
                return col
    PRIORITY = ["revenue","sales","amount","value","total","profit","cost","price",
                "salary","income","spend","budget","score","qty","quantity"]
    for kw in PRIORITY:
        for col in numeric_cols:
            if kw in col.lower():
                return col
    return max(numeric_cols, key=lambda c: df[c].sum())


def fmt_number(n) -> str:
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
    if file_name.lower().endswith(".csv"):
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
# KPI GENERATION  (config-aware)
# ─────────────────────────────────────────────
def build_kpis(df: pd.DataFrame, schema: dict, primary: str | None, config: dict = None) -> list[dict]:
    kpis = []
    colors = CHART_PALETTE

    # If Gemini recommended specific KPIs, use them first
    if config and config.get("recommended_kpis"):
        for i, kpi_cfg in enumerate(config["recommended_kpis"][:6]):
            col = kpi_cfg.get("column") or kpi_cfg.get("field")
            agg = kpi_cfg.get("aggregation", "sum").lower()
            label = kpi_cfg.get("label", col)
            if col and col in df.columns:
                try:
                    if agg == "sum":
                        val = df[col].sum()
                        sub = f"avg {fmt_number(df[col].mean())}"
                    elif agg == "avg" or agg == "mean":
                        val = df[col].mean()
                        sub = f"max {fmt_number(df[col].max())}"
                    elif agg == "count":
                        val = df[col].count()
                        sub = "total count"
                    elif agg == "max":
                        val = df[col].max()
                        sub = f"min {fmt_number(df[col].min())}"
                    else:
                        val = df[col].sum()
                        sub = f"avg {fmt_number(df[col].mean())}"
                    kpis.append({"label": label, "value": fmt_number(val), "sub": sub,
                                 "color": colors[i % len(colors)]})
                except Exception:
                    pass

    # Fallback / supplement with auto-detected KPIs
    if len(kpis) < 2:
        kpis.append({"label":"Total Records","value":fmt_number(len(df)),"sub":"rows in dataset","color":colors[0]})
        if primary:
            total = df[primary].sum()
            avg   = df[primary].mean()
            kpis.append({"label":f"Total {primary}","value":fmt_number(total),"sub":f"avg {fmt_number(avg)}","color":colors[1]})
        for col in schema["numeric"]:
            if col == primary or len(kpis) >= 7:
                break
            kpis.append({"label":f"Avg {col}","value":fmt_number(df[col].mean()),
                         "sub":f"max {fmt_number(df[col].max())}","color":colors[len(kpis)%len(colors)]})
        for col in schema["categorical"][:3]:
            if len(kpis) >= 8:
                break
            kpis.append({"label":f"Unique {col}","value":fmt_number(df[col].nunique()),
                         "sub":"distinct values","color":colors[len(kpis)%len(colors)]})
        if schema["date"]:
            dcol = schema["date"][0]
            mn, mx = df[dcol].min(), df[dcol].max()
            if pd.notna(mn) and pd.notna(mx):
                kpis.append({"label":"Date Range","value":str((mx-mn).days)+" d",
                             "sub":f"{mn.strftime('%b %Y')} – {mx.strftime('%b %Y')}",
                             "color":colors[len(kpis)%len(colors)]})

    return kpis[:8]


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
def chart_time_series(df: pd.DataFrame, date_col: str, num_col: str) -> go.Figure:
    tmp = df[[date_col, num_col]].dropna()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp = tmp.set_index(date_col).resample("ME")[num_col].sum().reset_index()
    fig = px.area(tmp, x=date_col, y=num_col, color_discrete_sequence=[CHART_PALETTE[0]])
    fig.update_traces(fill="tozeroy", line_width=2, fillcolor="rgba(79,142,247,0.15)")
    return apply_template(fig, f"{num_col} Over Time")


def chart_category_bar(df: pd.DataFrame, cat_col: str, num_col: str, top_n: int = 15) -> go.Figure:
    grp = df.groupby(cat_col, observed=True)[num_col].sum().nlargest(top_n).reset_index()
    grp = grp.sort_values(num_col, ascending=True)
    fig = px.bar(grp, x=num_col, y=cat_col, orientation="h",
                 color=num_col, color_continuous_scale=["#1e3a5f","#4f8ef7"])
    fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title=num_col)
    return apply_template(fig, f"Top {top_n} {cat_col} by {num_col}")


def chart_distribution(df: pd.DataFrame, num_col: str) -> go.Figure:
    series = df[num_col].dropna()
    fig = px.histogram(series, nbins=30, color_discrete_sequence=[CHART_PALETTE[2]])
    fig.update_traces(marker_line_width=0)
    return apply_template(fig, f"Distribution of {num_col}")


def chart_category_pie(df: pd.DataFrame, cat_col: str, num_col: str | None) -> go.Figure:
    if num_col:
        grp = df.groupby(cat_col, observed=True)[num_col].sum().reset_index()
        vals, names = num_col, cat_col
    else:
        grp = df[cat_col].value_counts().reset_index()
        grp.columns = [cat_col, "count"]
        vals, names = "count", cat_col
    grp = grp.nlargest(10, vals)
    fig = px.pie(grp, values=vals, names=names, hole=.45,
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(textposition="outside", textinfo="percent+label")
    return apply_template(fig, f"{cat_col} Breakdown")


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
    kw = dict(color=color_col) if color_col else {}
    fig = px.scatter(df.sample(min(2000, len(df))), x=x_col, y=y_col,
                     opacity=.7, color_discrete_sequence=CHART_PALETTE, **kw)
    return apply_template(fig, f"{y_col} vs {x_col}")


def chart_cat_count(df: pd.DataFrame, cat_col: str) -> go.Figure:
    grp = df[cat_col].value_counts().nlargest(15).reset_index()
    grp.columns = [cat_col, "count"]
    fig = px.bar(grp, x=cat_col, y="count", color="count",
                 color_continuous_scale=["#1e3a5f","#a78bfa"])
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
    return apply_template(fig, f"{cat_col} Frequency")


def chart_box(df: pd.DataFrame, cat_col: str, num_col: str) -> go.Figure:
    top = df[cat_col].value_counts().nlargest(10).index
    tmp = df[df[cat_col].isin(top)]
    fig = px.box(tmp, x=cat_col, y=num_col, color=cat_col,
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    return apply_template(fig, f"{num_col} Distribution by {cat_col}")


def chart_from_config(df: pd.DataFrame, chart_cfg: dict, schema: dict) -> go.Figure | None:
    """Build a chart from Gemini config entry."""
    chart_type = chart_cfg.get("type", "").lower()
    x = chart_cfg.get("x") or chart_cfg.get("x_axis")
    y = chart_cfg.get("y") or chart_cfg.get("y_axis")
    color = chart_cfg.get("color")
    title = chart_cfg.get("title", "")

    # Validate columns exist
    if x and x not in df.columns:
        x = None
    if y and y not in df.columns:
        y = None
    if color and color not in df.columns:
        color = None

    try:
        if chart_type == "bar" and x and y:
            grp = df.groupby(x, observed=True)[y].sum().nlargest(15).reset_index()
            fig = px.bar(grp, x=x, y=y, color_discrete_sequence=CHART_PALETTE, title=title)
            return apply_template(fig, title)
        elif chart_type == "line" and x and y:
            fig = px.line(df, x=x, y=y, color=color, color_discrete_sequence=CHART_PALETTE)
            return apply_template(fig, title)
        elif chart_type == "pie" and x:
            return chart_category_pie(df, x, y)
        elif chart_type == "scatter" and x and y:
            return chart_scatter(df, x, y, color)
        elif chart_type == "histogram" and x:
            return chart_distribution(df, x)
        elif chart_type == "heatmap" and schema.get("date") and y:
            return chart_monthly_heatmap(df, schema["date"][0], y)
        elif chart_type == "box" and x and y:
            return chart_box(df, x, y)
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────
# INSIGHTS
# ─────────────────────────────────────────────
def generate_insights(df: pd.DataFrame, schema: dict, primary: str | None,
                      config: dict = None) -> list[dict]:
    insights = []
    cat_cols = schema["categorical"]
    num_cols = schema["numeric"]

    # Gemini insights take priority
    if config and config.get("insights"):
        for ins in config["insights"][:6]:
            insights.append({
                "icon": ins.get("icon", "💡"),
                "title": ins.get("title", "Insight"),
                "body": ins.get("body", ins.get("text", ""))
            })

    # Auto-generated insights
    if primary and cat_cols and len(insights) < 4:
        grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
        top_val, top_name = grp.max(), grp.idxmax()
        pct = grp.max() / grp.sum() * 100
        insights.append({"icon":"🏆","title":"Top Performer",
                          "body":f"<b>{top_name}</b> leads with {fmt_number(top_val)} ({pct:.1f}% of total)."})
        bot_name = grp.idxmin()
        bot_val  = grp.min()
        insights.append({"icon":"⚠️","title":"Needs Attention",
                          "body":f"<b>{bot_name}</b> has the lowest {primary} at {fmt_number(bot_val)}."})

    if primary and schema["date"] and len(insights) < 6:
        dcol = schema["date"][0]
        tmp = df[[dcol, primary]].dropna()
        tmp[dcol] = pd.to_datetime(tmp[dcol])
        monthly = tmp.set_index(dcol).resample("ME")[primary].sum()
        if len(monthly) >= 2:
            peak_m = monthly.idxmax()
            insights.append({"icon":"📈","title":"Peak Month",
                              "body":f"Highest {primary} in <b>{peak_m.strftime('%B %Y')}</b> at {fmt_number(monthly.max())}."})
            last2 = monthly.iloc[-2:]
            if len(last2) == 2:
                chg = (last2.iloc[-1] - last2.iloc[-2]) / (abs(last2.iloc[-2]) + 1e-9) * 100
                arrow = "↑" if chg >= 0 else "↓"
                insights.append({"icon":"📊","title":"Recent Trend",
                                  "body":f"Last month changed by <b>{arrow} {abs(chg):.1f}%</b> vs previous month."})

    if primary and len(insights) < 7:
        z = (df[primary] - df[primary].mean()) / (df[primary].std() + 1e-9)
        outlier_count = (z.abs() > 3).sum()
        if outlier_count > 0:
            insights.append({"icon":"🔍","title":"Outliers Detected",
                              "body":f"<b>{outlier_count}</b> records fall outside 3 standard deviations."})

    if len(num_cols) >= 2 and len(insights) < 8:
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

    return insights[:8]


# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
def render_sidebar_filters(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    st.sidebar.markdown("## ⚙ Filters")
    filtered = df.copy()

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

    if schema["numeric"]:
        num_col = schema["numeric"][0]
        col_data = df[num_col].dropna()
        if not col_data.empty:
            mn, mx = float(col_data.min()), float(col_data.max())
            if mn < mx:
                sel = st.sidebar.slider(f"{num_col} Range", mn, mx, (mn, mx), key=f"slider_{num_col}")
                filtered = filtered[(filtered[num_col] >= sel[0]) & (filtered[num_col] <= sel[1])]

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='color:#64748b;font-size:.8rem;'>Showing "
        f"<b style='color:#e2e8f0'>{len(filtered):,}</b> of {len(df):,} rows</div>",
        unsafe_allow_html=True
    )
    return filtered


# ─────────────────────────────────────────────
# SECTION HEADER HELPER
# ─────────────────────────────────────────────
def section_header(title: str, badge: str = ""):
    badge_html = f'<span class="section-pill">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="section-head">
        <h2>{title}</h2>
        {badge_html}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RENDER DASHBOARD (core logic)
# ─────────────────────────────────────────────
def render_dashboard(df_raw: pd.DataFrame, file_label: str, config: dict = None,
                     dashboard_meta: dict = None):
    """Main dashboard rendering – call with loaded dataframe + optional config."""

    schema  = detect_schema(df_raw)
    df_raw  = coerce_dates(df_raw, schema["date"])
    primary = pick_primary_measure(df_raw, schema["numeric"], config)

    # Sidebar filters
    df = render_sidebar_filters(df_raw, schema)

    # ── Sidebar branding ──
    with st.sidebar:
        if dashboard_meta:
            expires = dashboard_meta.get("expires_at", "")
            if expires:
                try:
                    exp = datetime.fromisoformat(expires.replace("Z",""))
                    days_left = (exp - datetime.now()).days
                    color = "#34d399" if days_left > 5 else "#f59e0b" if days_left > 1 else "#f87171"
                    st.markdown(
                        f"<div style='font-size:.75rem;color:{color};margin-top:8px'>"
                        f"⏱ Expires in {days_left} day{'s' if days_left != 1 else ''}</div>",
                        unsafe_allow_html=True
                    )
                except Exception:
                    pass

    # ── Header ──
    dataset_type = config.get("dataset_type", "") if config else ""
    type_badge = f" · {dataset_type.upper()}" if dataset_type else ""
    st.markdown(f"""
    <div style='padding:.5rem 0 1rem'>
        <div class='dash-title'>{file_label}{type_badge}</div>
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

    # ── Custom request banner ──
    if dashboard_meta and dashboard_meta.get("custom_request"):
        st.info(f"🎯 **Custom request:** {dashboard_meta['custom_request']}")

    # ── KPIs ──
    kpis = build_kpis(df, schema, primary, config)
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

    # ── CHARTS ──
    section_header("Visualizations",
                   "AI-selected" if config and config.get("recommended_charts") else "Auto-selected")

    has_date = bool(schema["date"])
    has_num  = bool(schema["numeric"])
    has_cat  = bool(schema["categorical"])
    rendered = 0

    # If Gemini provided chart config, render those first
    if config and config.get("recommended_charts"):
        charts_from_config = []
        for ch in config["recommended_charts"]:
            fig = chart_from_config(df, ch, schema)
            if fig:
                charts_from_config.append(fig)

        # Render in pairs
        for i in range(0, len(charts_from_config), 2):
            if i + 1 < len(charts_from_config):
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(charts_from_config[i],   use_container_width=True)
                with c2: st.plotly_chart(charts_from_config[i+1], use_container_width=True)
            else:
                st.plotly_chart(charts_from_config[i], use_container_width=True)
            rendered += 1

    # Auto charts (fill in gaps / fallback)
    if rendered == 0:
        if has_date and primary:
            c1, c2 = st.columns([3, 2])
            with c1:
                st.plotly_chart(chart_time_series(df, schema["date"][0], primary),
                                use_container_width=True)
            with c2:
                if has_cat:
                    st.plotly_chart(chart_category_pie(df, schema["categorical"][0], primary),
                                    use_container_width=True)
                else:
                    st.plotly_chart(chart_distribution(df, primary), use_container_width=True)
            rendered += 1

        if has_cat and primary:
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(chart_category_bar(df, schema["categorical"][0], primary),
                                use_container_width=True)
            with c2:
                st.plotly_chart(chart_distribution(df, primary), use_container_width=True)
            rendered += 1

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

    # ── INSIGHTS ──
    section_header("Automated Insights",
                   "Gemini AI" if config and config.get("insights") else "AI-style")
    insights = generate_insights(df, schema, primary, config)
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

    # ── DATA PREVIEW ──
    with st.expander("📋 Data Preview", expanded=False):
        st.dataframe(df.head(200), use_container_width=True, height=300)

    # ── SCHEMA ──
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


# ─────────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────────
def render_welcome():
    st.markdown("""
    <div style='padding:2rem 0;'>
        <div class='dash-title'>Universal Dashboard</div>
        <div class='dash-sub'>Drop any CSV or Excel file — instant analytics.</div>
    </div>
    <div class='upload-wrapper'>
        <div class='upload-icon'>📂</div>
        <div class='upload-title'>Upload your dataset</div>
        <div class='upload-sub'>Supports CSV, XLSX, XLS · Max 200 MB</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    # ── Get dashboard ID from URL params ──
    query_params  = st.query_params
    dashboard_id  = query_params.get("dashboard") or query_params.get("id")

    # ── Sidebar branding ──
    with st.sidebar:
        st.markdown("""
        <div style='margin-bottom:1.5rem'>
            <div style='font-size:1.15rem;font-weight:700;color:#e2e8f0'>📊 Dashboard</div>
            <div style='font-size:.75rem;color:#64748b;margin-top:2px'>Universal Data Explorer</div>
        </div>
        """, unsafe_allow_html=True)

        # Manual upload (dev/testing mode only when no dashboard_id)
        if not dashboard_id:
            uploaded = st.file_uploader(
                "Upload Dataset",
                type=["csv","xlsx","xls"],
                label_visibility="collapsed"
            )
        else:
            uploaded = None

    # ══════════════════════════════════
    # MODE 1: URL-based (Telegram flow)
    # ══════════════════════════════════
    if dashboard_id:
        # Check expiration first
        if check_dashboard_expired(dashboard_id):
            st.markdown("""
            <div class='expired-banner'>
                <div style='font-size:3rem;margin-bottom:1rem'>⏰</div>
                <div style='font-size:1.3rem;font-weight:700;color:#f87171'>Dashboard Expired</div>
                <div style='color:#64748b;margin-top:.5rem'>
                    This dashboard was available for 15 days and has now expired.<br>
                    Please upload a new file via the Telegram bot.
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        # Fetch metadata from Supabase
        with st.spinner("Loading dashboard…"):
            meta = get_dashboard_meta(dashboard_id)

        if not meta:
            st.error("❌ Dashboard not found. It may have been deleted or the link is invalid.")
            return

        # Load file from Supabase Storage
        storage_path = meta.get("storage_path", "")
        file_name    = meta.get("file_name", "dataset.csv")
        config       = meta.get("gemini_response") or meta.get("config_json") or {}

        with st.spinner("Loading dataset…"):
            file_bytes = load_from_supabase(storage_path)

        if not file_bytes:
            st.error("❌ Could not load dataset. Storage may be unavailable.")
            return

        try:
            df_raw = load_data(file_bytes, file_name)
        except Exception as e:
            st.error(f"❌ Could not parse file: {e}")
            return

        file_label = file_name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
        render_dashboard(df_raw, file_label, config=config, dashboard_meta=meta)

    # ══════════════════════════════════
    # MODE 2: Manual upload (dev mode)
    # ══════════════════════════════════
    elif uploaded is not None:
        with st.spinner("Analyzing dataset…"):
            try:
                df_raw = load_data(uploaded.read(), uploaded.name)
            except Exception as e:
                st.error(f"Could not load file: {e}")
                return
        file_label = uploaded.name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
        render_dashboard(df_raw, file_label)

    # ══════════════════════════════════
    # MODE 3: Welcome screen
    # ══════════════════════════════════
    else:
        render_welcome()


if __name__ == "__main__":
    main()

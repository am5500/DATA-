"""
Dynamic Dashboard Generator – Telegram Bot Edition
====================================================
Production-ready Streamlit app.
- Loads dataset from Supabase Storage via dashboard_id URL param
- Falls back to manual upload for local testing
- Reads config.json (Gemini AI output) to customize charts/KPIs
- STATIC generator: AI never modifies this file
- Premium enterprise UI with dark/light mode, multi-page, advanced charts
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
    page_title="Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME DEFINITIONS
# ─────────────────────────────────────────────
DARK_THEME = {
    "bg":         "#0a0c12",
    "surface":    "#111318",
    "card":       "#161921",
    "card2":      "#1c2030",
    "border":     "rgba(255,255,255,0.07)",
    "border2":    "rgba(255,255,255,0.12)",
    "accent1":    "#4f8ef7",
    "accent2":    "#a78bfa",
    "accent3":    "#34d399",
    "accent4":    "#f59e0b",
    "text":       "#e2e8f0",
    "text2":      "#94a3b8",
    "muted":      "#64748b",
    "danger":     "#f87171",
    "success":    "#34d399",
    "chart_bg":   "rgba(0,0,0,0)",
    "grid":       "rgba(255,255,255,0.05)",
    "chart_font": "#94a3b8",
}

LIGHT_THEME = {
    "bg":         "#f0f2f7",
    "surface":    "#e8ebf2",
    "card":       "#ffffff",
    "card2":      "#f8f9fc",
    "border":     "rgba(0,0,0,0.08)",
    "border2":    "rgba(0,0,0,0.14)",
    "accent1":    "#2563eb",
    "accent2":    "#7c3aed",
    "accent3":    "#059669",
    "accent4":    "#d97706",
    "text":       "#0f172a",
    "text2":      "#374151",
    "muted":      "#6b7280",
    "danger":     "#dc2626",
    "success":    "#059669",
    "chart_bg":   "rgba(0,0,0,0)",
    "grid":       "rgba(0,0,0,0.05)",
    "chart_font": "#374151",
}

def get_theme():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True
    return DARK_THEME if st.session_state.dark_mode else LIGHT_THEME

def inject_css(t: dict):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {{
    --bg:       {t["bg"]};
    --surface:  {t["surface"]};
    --card:     {t["card"]};
    --card2:    {t["card2"]};
    --border:   {t["border"]};
    --border2:  {t["border2"]};
    --accent1:  {t["accent1"]};
    --accent2:  {t["accent2"]};
    --accent3:  {t["accent3"]};
    --accent4:  {t["accent4"]};
    --text:     {t["text"]};
    --text2:    {t["text2"]};
    --muted:    {t["muted"]};
    --danger:   {t["danger"]};
    --success:  {t["success"]};
    --radius:   14px;
    --radius-sm:8px;
    --shadow:   0 4px 24px rgba(0,0,0,0.18);
    --shadow-lg:0 8px 40px rgba(0,0,0,0.28);
}}

html, body, .stApp {{
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text);
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: var(--surface) !important;
    border-right: 1px solid var(--border2);
}}
[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {{
    background: var(--card) !important;
    border-color: var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.9rem !important;
}}
[data-testid="stSidebar"] label {{
    color: var(--text2) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}}

/* Hide default header */
header[data-testid="stHeader"] {{ display: none; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--border2); border-radius: 3px; }}

/* ── GLASS CARD ── */
.glass-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    box-shadow: var(--shadow);
    transition: border-color .2s, box-shadow .2s, transform .2s;
}}
.glass-card:hover {{
    border-color: var(--border2);
    box-shadow: var(--shadow-lg);
}}

/* ── EXECUTIVE SUMMARY ── */
.exec-summary {{
    background: linear-gradient(135deg, {t["card"]} 0%, {t["card2"]} 100%);
    border: 1px solid var(--border2);
    border-left: 4px solid var(--accent1);
    border-radius: var(--radius);
    padding: 1.8rem 2rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}}
.exec-summary::before {{
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, {t["accent1"]}18 0%, transparent 70%);
    pointer-events: none;
}}
.exec-summary-label {{
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent1);
    margin-bottom: 0.7rem;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.exec-summary-title {{
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.9rem;
    line-height: 1.3;
}}
.exec-summary-body {{
    font-size: 0.96rem;
    color: var(--text2);
    line-height: 1.65;
}}
.exec-summary-body strong {{ color: var(--text); }}

/* ── KPI CARDS ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 2rem;
}}
.kpi-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.5rem;
    position: relative;
    overflow: hidden;
    cursor: default;
    transition: transform .2s, border-color .2s, box-shadow .2s;
}}
.kpi-card:hover {{
    transform: translateY(-3px);
    border-color: var(--border2);
    box-shadow: var(--shadow-lg);
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent-color, var(--accent1));
    border-radius: var(--radius) var(--radius) 0 0;
}}
.kpi-card::after {{
    content: '';
    position: absolute;
    bottom: -20px; right: -20px;
    width: 80px; height: 80px;
    background: radial-gradient(circle, var(--accent-color, var(--accent1))14 0%, transparent 70%);
    pointer-events: none;
}}
.kpi-label {{
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.55rem;
}}
.kpi-value {{
    font-size: 2.1rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.1;
    font-family: 'DM Mono', monospace;
    letter-spacing: -0.02em;
}}
.kpi-delta {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 99px;
    margin-top: 0.5rem;
}}
.kpi-delta.pos {{
    background: rgba(52,211,153,0.12);
    color: var(--success);
}}
.kpi-delta.neg {{
    background: rgba(248,113,113,0.12);
    color: var(--danger);
}}
.kpi-delta.neu {{
    background: rgba(148,163,184,0.1);
    color: var(--muted);
}}
.kpi-sub {{
    font-size: 0.76rem;
    color: var(--muted);
    margin-top: 0.35rem;
}}
.kpi-period {{
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.2rem;
    font-style: italic;
}}

/* ── SECTION HEADER ── */
.section-head {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2rem 0 1.2rem;
}}
.section-head h2 {{
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text);
    margin: 0;
    letter-spacing: -0.01em;
}}
.section-pill {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 11px;
    border-radius: 99px;
    background: rgba(79,142,247,0.12);
    color: var(--accent1);
    border: 1px solid rgba(79,142,247,0.22);
}}

/* ── DASHBOARD TITLE ── */
.dash-title {{
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(120deg, var(--accent1), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}}
.dash-sub {{
    color: var(--muted);
    font-size: 1rem;
    margin-top: 0.35rem;
    font-weight: 400;
}}

/* ── META BADGES ── */
.meta-row {{ display: flex; gap: 8px; margin-top: 1rem; flex-wrap: wrap; }}
.meta-badge {{
    font-size: 0.78rem; font-weight: 500;
    padding: 5px 14px; border-radius: 99px;
    background: var(--card); border: 1px solid var(--border2);
    color: var(--muted);
}}
.meta-badge span {{ color: var(--text); font-weight: 700; }}

/* ── INSIGHT CARDS ── */
.insight-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 14px;
    margin-bottom: 1rem;
}}
.insight-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.1rem 1.3rem;
    display: flex; gap: 14px; align-items: flex-start;
    transition: border-color .2s, transform .2s;
}}
.insight-card:hover {{
    border-color: var(--border2);
    transform: translateY(-2px);
}}
.insight-icon {{ font-size: 1.6rem; line-height: 1; flex-shrink: 0; margin-top: 2px; }}
.insight-title {{
    font-size: 0.74rem; font-weight: 700; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem;
}}
.insight-body {{ font-size: 0.9rem; color: var(--text2); line-height: 1.5; }}
.insight-body strong {{ color: var(--text); }}

/* ── TOP/BOTTOM TABLE ── */
.rank-table {{ width: 100%; border-collapse: collapse; }}
.rank-table th {{
    font-size: 0.74rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; color: var(--muted);
    padding: 8px 12px; border-bottom: 1px solid var(--border2);
    text-align: left;
}}
.rank-table td {{
    font-size: 0.88rem; color: var(--text2);
    padding: 9px 12px; border-bottom: 1px solid var(--border);
}}
.rank-table tr:last-child td {{ border-bottom: none; }}
.rank-table .rank-num {{
    font-size: 0.72rem; font-weight: 700; color: var(--muted);
    font-family: 'DM Mono', monospace;
}}
.rank-table .rank-val {{
    font-family: 'DM Mono', monospace; font-weight: 600;
    color: var(--text);
}}
.rank-badge {{
    display: inline-block; padding: 2px 8px; border-radius: 99px;
    font-size: 0.72rem; font-weight: 600;
}}
.rank-badge.top {{ background: rgba(52,211,153,0.12); color: var(--success); }}
.rank-badge.bot {{ background: rgba(248,113,113,0.12); color: var(--danger); }}

/* ── AI INSIGHTS PAGE ── */
.ai-section {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    transition: border-color .2s;
}}
.ai-section:hover {{ border-color: var(--border2); }}
.ai-section-label {{
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--accent1);
    margin-bottom: 0.7rem; display: flex; align-items: center; gap: 6px;
}}
.ai-section-content {{
    font-size: 0.94rem; color: var(--text2); line-height: 1.65;
}}
.ai-section-content strong {{ color: var(--text); }}
.ai-list {{ list-style: none; padding: 0; margin: 0.5rem 0 0; }}
.ai-list li {{
    padding: 6px 0 6px 20px; position: relative;
    font-size: 0.91rem; color: var(--text2); border-bottom: 1px solid var(--border);
}}
.ai-list li:last-child {{ border-bottom: none; }}
.ai-list li::before {{
    content: '→'; position: absolute; left: 0;
    color: var(--accent1); font-weight: 700;
}}

/* ── TIME COMPARISON ── */
.comparison-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
    margin: 1rem 0;
}}
.comparison-card {{
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 1rem 1.2rem;
    text-align: center;
}}
.comparison-label {{
    font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--muted); margin-bottom: 0.4rem;
}}
.comparison-value {{
    font-size: 1.5rem; font-weight: 700; font-family: 'DM Mono', monospace;
    line-height: 1.1;
}}
.comparison-value.pos {{ color: var(--success); }}
.comparison-value.neg {{ color: var(--danger); }}
.comparison-value.neu {{ color: var(--text); }}

/* ── NAV TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: var(--radius-sm) !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 8px 20px !important;
    transition: all .2s !important;
}}
.stTabs [aria-selected="true"] {{
    background: var(--card) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding-top: 1.5rem !important;
}}

/* ── FILTER SUMMARY ── */
.filter-summary {{
    background: rgba(79,142,247,0.08);
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: var(--radius-sm);
    padding: 8px 14px;
    font-size: 0.82rem;
    color: var(--accent1);
    margin-top: 8px;
    font-weight: 500;
}}

/* ── MISC ── */
.divider {{ border: none; border-top: 1px solid var(--border); margin: 1.8rem 0; }}
.js-plotly-plot {{ border-radius: var(--radius); overflow: hidden; }}

/* ── EXPIRED BANNER ── */
.expired-banner {{
    background: rgba(248,113,113,0.08);
    border: 1px solid rgba(248,113,113,0.25);
    border-radius: var(--radius);
    padding: 2.5rem;
    text-align: center;
    margin: 4rem auto;
    max-width: 520px;
}}

/* ── UPLOAD ── */
.upload-wrapper {{
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 4rem 2.5rem;
    border: 2px dashed rgba(79,142,247,0.25);
    border-radius: var(--radius); background: var(--card);
    text-align: center; margin: 2rem auto; max-width: 580px;
    transition: border-color .2s;
}}
.upload-wrapper:hover {{ border-color: rgba(79,142,247,0.45); }}
.upload-icon {{ font-size: 3.5rem; margin-bottom: 1.2rem; }}
.upload-title {{ font-size: 1.25rem; font-weight: 700; color: var(--text); }}
.upload-sub {{ font-size: 0.9rem; color: var(--muted); margin-top: 0.5rem; }}

/* Form inputs */
div[data-testid="stFileUploader"] label {{ color: var(--text) !important; }}
.stSelectbox label, .stMultiSelect label, .stDateInput label,
.stSlider label, .stCheckbox label {{
    color: var(--muted) !important; font-size: 0.82rem !important;
    font-weight: 600 !important; letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}}
.stSelectbox > div > div, .stMultiSelect > div > div {{
    background: var(--card) !important;
    border-color: var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
}}
button[kind="secondary"] {{
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    transition: all .2s !important;
}}
button[kind="secondary"]:hover {{
    border-color: var(--accent1) !important;
    color: var(--accent1) !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CHART PALETTE + PLOTLY TEMPLATE
# ─────────────────────────────────────────────
CHART_PALETTE = ["#4f8ef7","#a78bfa","#34d399","#f59e0b","#f87171",
                 "#38bdf8","#fb923c","#e879f9","#a3e635","#2dd4bf"]

def get_plotly_layout(t: dict) -> dict:
    return dict(
        paper_bgcolor=t["chart_bg"],
        plot_bgcolor=t["chart_bg"],
        font=dict(family="Inter", color=t["chart_font"], size=12),
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=12),
        ),
        xaxis=dict(
            gridcolor=t["grid"],
            zerolinecolor=t["grid"],
            linecolor=t["grid"],
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor=t["grid"],
            zerolinecolor=t["grid"],
            linecolor=t["grid"],
            tickfont=dict(size=11),
        ),
        colorway=CHART_PALETTE,
        hoverlabel=dict(
            bgcolor=t["card"],
            font_color=t["text"],
            font_size=12,
            bordercolor=t["border2"],
        ),
    )

def apply_template(fig, title="", t: dict = None):
    if t is None:
        t = get_theme()
    layout = get_plotly_layout(t)
    fig.update_layout(
        **layout,
        title=dict(
            text=title,
            font=dict(color=t["text"], size=15, family="Inter"),
            x=0,
            xanchor="left",
        ),
    )
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


def fmt_pct(n) -> str:
    if pd.isna(n):
        return "—"
    return f"{float(n):+.1f}%"


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
# TIME COMPARISON ENGINE
# ─────────────────────────────────────────────
def compute_time_comparisons(df: pd.DataFrame, date_col: str, value_col: str) -> dict:
    """Calculate YoY, MoM, QoQ and period comparisons."""
    result = {}
    try:
        tmp = df[[date_col, value_col]].dropna().copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col])
        tmp = tmp.set_index(date_col)

        # Monthly series
        monthly = tmp.resample("ME")[value_col].sum()
        if len(monthly) < 2:
            return result

        # MoM
        if len(monthly) >= 2:
            curr_m = monthly.iloc[-1]
            prev_m = monthly.iloc[-2]
            mom = (curr_m - prev_m) / (abs(prev_m) + 1e-9) * 100
            result["mom"] = {"value": mom, "label": "Month over Month",
                             "curr": curr_m, "prev": prev_m,
                             "period": monthly.index[-1].strftime("%b %Y")}

        # QoQ
        quarterly = tmp.resample("QE")[value_col].sum()
        if len(quarterly) >= 2:
            curr_q = quarterly.iloc[-1]
            prev_q = quarterly.iloc[-2]
            qoq = (curr_q - prev_q) / (abs(prev_q) + 1e-9) * 100
            result["qoq"] = {"value": qoq, "label": "Quarter over Quarter",
                              "curr": curr_q, "prev": prev_q,
                              "period": f"Q{quarterly.index[-1].quarter} {quarterly.index[-1].year}"}

        # YoY
        yearly = tmp.resample("YE")[value_col].sum()
        if len(yearly) >= 2:
            curr_y = yearly.iloc[-1]
            prev_y = yearly.iloc[-2]
            yoy = (curr_y - prev_y) / (abs(prev_y) + 1e-9) * 100
            result["yoy"] = {"value": yoy, "label": "Year over Year",
                              "curr": curr_y, "prev": prev_y,
                              "period": str(yearly.index[-1].year)}

        # Best / Worst period
        result["best_period"] = {
            "label": "Best Month",
            "value": monthly.max(),
            "period": monthly.idxmax().strftime("%b %Y"),
        }
        result["worst_period"] = {
            "label": "Worst Month",
            "value": monthly.min(),
            "period": monthly.idxmin().strftime("%b %Y"),
        }

    except Exception:
        pass
    return result


# ─────────────────────────────────────────────
# EXECUTIVE SUMMARY GENERATOR
# ─────────────────────────────────────────────
def generate_executive_summary(df: pd.DataFrame, schema: dict, primary: str | None,
                                config: dict = None, file_label: str = "") -> str:
    """Generate an AI-style executive narrative from data."""
    # Check if config provides a summary
    if config and config.get("summary"):
        return config["summary"]

    parts = []
    num_cols = schema["numeric"]
    cat_cols = schema["categorical"]
    date_cols = schema["date"]

    if primary and primary in df.columns:
        total = df[primary].sum()
        parts.append(f"Total <strong>{primary}</strong> stands at <strong>{fmt_number(total)}</strong> across {len(df):,} records.")

    if date_cols and primary:
        try:
            tmp = df[[date_cols[0], primary]].dropna().copy()
            tmp[date_cols[0]] = pd.to_datetime(tmp[date_cols[0]])
            monthly = tmp.set_index(date_cols[0]).resample("ME")[primary].sum()
            if len(monthly) >= 2:
                mom = (monthly.iloc[-1] - monthly.iloc[-2]) / (abs(monthly.iloc[-2]) + 1e-9) * 100
                direction = "increased" if mom >= 0 else "declined"
                arrow = "↑" if mom >= 0 else "↓"
                parts.append(f"Performance <strong>{direction} by {arrow} {abs(mom):.1f}%</strong> month-over-month.")
                peak = monthly.idxmax()
                parts.append(f"The strongest period was <strong>{peak.strftime('%B %Y')}</strong> with {fmt_number(monthly.max())}.")
        except Exception:
            pass

    if cat_cols and primary:
        try:
            grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
            top_cat = grp.idxmax()
            top_pct = grp.max() / grp.sum() * 100
            parts.append(f"The leading <strong>{cat_cols[0]}</strong> is <strong>{top_cat}</strong>, contributing {top_pct:.1f}% of total {primary}.")
        except Exception:
            pass

    if len(num_cols) >= 2:
        parts.append(f"The dataset spans <strong>{len(num_cols)} numeric dimensions</strong> and <strong>{len(cat_cols)} categorical segments</strong>.")

    return " ".join(parts) if parts else f"Dataset contains <strong>{len(df):,} records</strong> across <strong>{len(df.columns)} dimensions</strong>."


# ─────────────────────────────────────────────
# KPI GENERATION (config-aware + growth arrows)
# ─────────────────────────────────────────────
def build_kpis(df: pd.DataFrame, schema: dict, primary: str | None,
               config: dict = None, time_comps: dict = None) -> list[dict]:
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
                    elif agg in ("avg", "mean"):
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

                    delta_val = None
                    delta_cls = "neu"
                    period_label = ""
                    if time_comps and col == primary and "mom" in time_comps:
                        delta_val = time_comps["mom"]["value"]
                        delta_cls = "pos" if delta_val >= 0 else "neg"
                        period_label = f"vs prev month · {time_comps['mom']['period']}"

                    kpis.append({
                        "label": label, "value": fmt_number(val), "sub": sub,
                        "color": colors[i % len(colors)],
                        "delta": delta_val, "delta_cls": delta_cls,
                        "period": period_label,
                    })
                except Exception:
                    pass

    # Fallback / supplement with auto-detected KPIs
    if len(kpis) < 2:
        kpis.append({
            "label": "Total Records", "value": fmt_number(len(df)),
            "sub": "rows in dataset", "color": colors[0],
            "delta": None, "delta_cls": "neu", "period": "",
        })
        if primary:
            total = df[primary].sum()
            avg   = df[primary].mean()
            mom_val = time_comps["mom"]["value"] if time_comps and "mom" in time_comps else None
            mom_cls = ("pos" if mom_val >= 0 else "neg") if mom_val is not None else "neu"
            mom_period = time_comps["mom"]["period"] if time_comps and "mom" in time_comps else ""
            kpis.append({
                "label": f"Total {primary}", "value": fmt_number(total),
                "sub": f"avg {fmt_number(avg)}", "color": colors[1],
                "delta": mom_val, "delta_cls": mom_cls, "period": f"vs prev month · {mom_period}" if mom_period else "",
            })

        for col in schema["numeric"]:
            if col == primary or len(kpis) >= 7:
                break
            kpis.append({
                "label": f"Avg {col}", "value": fmt_number(df[col].mean()),
                "sub": f"max {fmt_number(df[col].max())}", "color": colors[len(kpis) % len(colors)],
                "delta": None, "delta_cls": "neu", "period": "",
            })
        for col in schema["categorical"][:3]:
            if len(kpis) >= 8:
                break
            kpis.append({
                "label": f"Unique {col}", "value": fmt_number(df[col].nunique()),
                "sub": "distinct values", "color": colors[len(kpis) % len(colors)],
                "delta": None, "delta_cls": "neu", "period": "",
            })
        if schema["date"]:
            dcol = schema["date"][0]
            mn, mx = df[dcol].min(), df[dcol].max()
            if pd.notna(mn) and pd.notna(mx):
                kpis.append({
                    "label": "Date Range", "value": str((mx - mn).days) + " d",
                    "sub": f"{mn.strftime('%b %Y')} – {mx.strftime('%b %Y')}",
                    "color": colors[len(kpis) % len(colors)],
                    "delta": None, "delta_cls": "neu", "period": "",
                })

    # Add YoY / QoQ cards from time comparisons
    if time_comps:
        for key, badge in [("yoy", "YoY Growth"), ("qoq", "QoQ Growth")]:
            if key in time_comps and len(kpis) < 8:
                tc = time_comps[key]
                cls = "pos" if tc["value"] >= 0 else "neg"
                kpis.append({
                    "label": badge, "value": fmt_pct(tc["value"]),
                    "sub": f"{tc['period']}", "color": CHART_PALETTE[2] if cls == "pos" else CHART_PALETTE[4],
                    "delta": tc["value"], "delta_cls": cls, "period": "",
                })

    return kpis[:8]


def render_kpi_cards(kpis: list):
    html = '<div class="kpi-grid">'
    for kpi in kpis:
        delta_html = ""
        if kpi.get("delta") is not None:
            arrow = "↑" if kpi["delta"] >= 0 else "↓"
            delta_html = f'<div class="kpi-delta {kpi["delta_cls"]}">{arrow} {abs(kpi["delta"]):.1f}%</div>'

        period_html = f'<div class="kpi-period">{kpi["period"]}</div>' if kpi.get("period") else ""

        html += f"""
        <div class='kpi-card' style='--accent-color:{kpi["color"]}'>
            <div class='kpi-label'>{kpi["label"]}</div>
            <div class='kpi-value'>{kpi["value"]}</div>
            {delta_html}
            <div class='kpi-sub'>{kpi["sub"]}</div>
            {period_html}
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CHARTS (upgraded)
# ─────────────────────────────────────────────
def chart_time_series(df: pd.DataFrame, date_col: str, num_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    tmp = df[[date_col, num_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp = tmp.set_index(date_col).resample("ME")[num_col].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tmp[date_col], y=tmp[num_col],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor=f"rgba(79,142,247,0.10)",
        line=dict(color=CHART_PALETTE[0], width=2.5),
        marker=dict(size=5, color=CHART_PALETTE[0]),
        hovertemplate=f"<b>%{{x|%b %Y}}</b><br>{num_col}: %{{y:,.0f}}<extra></extra>",
    ))
    return apply_template(fig, f"📈 {num_col} Over Time", t)


def chart_area_comparison(df: pd.DataFrame, date_col: str, num_col: str,
                           cat_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    tmp = df[[date_col, num_col, cat_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    top_cats = df[cat_col].value_counts().nlargest(5).index.tolist()
    tmp = tmp[tmp[cat_col].isin(top_cats)]
    fig = go.Figure()
    for i, cat in enumerate(top_cats):
        sub = tmp[tmp[cat_col] == cat].set_index(date_col).resample("ME")[num_col].sum().reset_index()
        fig.add_trace(go.Scatter(
            x=sub[date_col], y=sub[num_col],
            name=str(cat), mode="lines",
            fill="tozeroy", line=dict(width=1.5, color=CHART_PALETTE[i % len(CHART_PALETTE)]),
            fillcolor=f"rgba({','.join(str(int(CHART_PALETTE[i%len(CHART_PALETTE)].lstrip('#')[j:j+2],16)) for j in (0,2,4))},0.07)",
            hovertemplate=f"<b>{cat}</b><br>%{{x|%b %Y}}: %{{y:,.0f}}<extra></extra>",
        ))
    return apply_template(fig, f"📊 {num_col} by {cat_col} Over Time", t)


def chart_category_bar(df: pd.DataFrame, cat_col: str, num_col: str,
                        top_n: int = 15, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    grp = df.groupby(cat_col, observed=True)[num_col].sum().nlargest(top_n).reset_index()
    grp = grp.sort_values(num_col, ascending=True)
    colors_bar = [CHART_PALETTE[0]] * len(grp)
    colors_bar[-1] = CHART_PALETTE[2]  # highlight top

    fig = go.Figure(go.Bar(
        x=grp[num_col], y=grp[cat_col],
        orientation="h",
        marker=dict(
            color=grp[num_col],
            colorscale=[[0, "#1a2744"], [1, CHART_PALETTE[0]]],
            line=dict(width=0),
        ),
        text=[fmt_number(v) for v in grp[num_col]],
        textposition="outside",
        textfont=dict(size=11, color=t["text2"]),
        hovertemplate=f"<b>%{{y}}</b><br>{num_col}: %{{x:,.0f}}<extra></extra>",
    ))
    fig.update_layout(xaxis_title=num_col, yaxis_title="", coloraxis_showscale=False)
    return apply_template(fig, f"🏆 Top {top_n} {cat_col} by {num_col}", t)


def chart_distribution(df: pd.DataFrame, num_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    series = df[num_col].dropna()
    fig = px.histogram(series, nbins=30, color_discrete_sequence=[CHART_PALETTE[2]])
    fig.update_traces(marker_line_width=0, opacity=0.85)
    return apply_template(fig, f"📊 Distribution of {num_col}", t)


def chart_category_pie(df: pd.DataFrame, cat_col: str, num_col: str | None,
                        t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    if num_col:
        grp = df.groupby(cat_col, observed=True)[num_col].sum().reset_index()
        vals, names = num_col, cat_col
    else:
        grp = df[cat_col].value_counts().reset_index()
        grp.columns = [cat_col, "count"]
        vals, names = "count", cat_col
    grp = grp.nlargest(10, vals)
    fig = px.pie(grp, values=vals, names=names, hole=.5,
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(
        textposition="outside", textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>",
    )
    fig.update_layout(showlegend=True)
    return apply_template(fig, f"🥧 {cat_col} Breakdown", t)


def chart_monthly_heatmap(df: pd.DataFrame, date_col: str, num_col: str,
                           t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    tmp = df[[date_col, num_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    tmp["Month"] = tmp[date_col].dt.month_name().str[:3]
    tmp["Year"]  = tmp[date_col].dt.year
    pivot = tmp.pivot_table(index="Month", columns="Year", values=num_col, aggfunc="sum")
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot = pivot.reindex([m for m in month_order if m in pivot.index])
    fig = px.imshow(
        pivot,
        color_continuous_scale=["#0d1a30", "#1e3a5f", CHART_PALETTE[0]],
        aspect="auto", text_auto=True,
    )
    fig.update_traces(
        hovertemplate="<b>%{y} %{x}</b><br>Value: %{z:,.0f}<extra></extra>",
    )
    return apply_template(fig, f"🗓 {num_col} Heatmap (Month × Year)", t)


def chart_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None,
                   t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    kw = dict(color=color_col) if color_col else {}
    fig = px.scatter(df.sample(min(2000, len(df))), x=x_col, y=y_col,
                     opacity=.65, color_discrete_sequence=CHART_PALETTE,
                     trendline="ols" if not color_col else None, **kw)
    return apply_template(fig, f"🔵 {y_col} vs {x_col}", t)


def chart_cat_count(df: pd.DataFrame, cat_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    grp = df[cat_col].value_counts().nlargest(15).reset_index()
    grp.columns = [cat_col, "count"]
    fig = go.Figure(go.Bar(
        x=grp[cat_col], y=grp["count"],
        marker=dict(
            color=grp["count"],
            colorscale=[[0, "#1a1e30"], [1, CHART_PALETTE[1]]],
            line=dict(width=0),
        ),
        text=[fmt_number(v) for v in grp["count"]],
        textposition="outside",
        textfont=dict(size=10, color=t["text2"]),
        hovertemplate="<b>%{x}</b><br>Count: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(xaxis_tickangle=-30, coloraxis_showscale=False)
    return apply_template(fig, f"📋 {cat_col} Frequency", t)


def chart_box(df: pd.DataFrame, cat_col: str, num_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    top = df[cat_col].value_counts().nlargest(10).index
    tmp = df[df[cat_col].isin(top)]
    fig = px.box(tmp, x=cat_col, y=num_col, color=cat_col,
                 color_discrete_sequence=CHART_PALETTE,
                 notched=True)
    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    return apply_template(fig, f"📦 {num_col} Distribution by {cat_col}", t)


def chart_treemap(df: pd.DataFrame, cat_col: str, num_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    grp = df.groupby(cat_col, observed=True)[num_col].sum().nlargest(20).reset_index()
    grp.columns = [cat_col, num_col]
    fig = px.treemap(
        grp, path=[cat_col], values=num_col,
        color=num_col,
        color_continuous_scale=["#1a2744", CHART_PALETTE[0]],
    )
    fig.update_traces(
        textfont=dict(size=13),
        hovertemplate="<b>%{label}</b><br>Value: %{value:,.0f}<extra></extra>",
    )
    fig.update_layout(coloraxis_showscale=False)
    return apply_template(fig, f"🟦 {cat_col} Treemap by {num_col}", t)


def chart_combo(df: pd.DataFrame, date_col: str, bar_col: str,
                line_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    tmp = df[[date_col, bar_col, line_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    monthly = tmp.set_index(date_col).resample("ME")[[bar_col, line_col]].sum().reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=monthly[date_col], y=monthly[bar_col],
        name=bar_col,
        marker_color=CHART_PALETTE[0],
        opacity=0.75,
        hovertemplate=f"<b>%{{x|%b %Y}}</b><br>{bar_col}: %{{y:,.0f}}<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=monthly[date_col], y=monthly[line_col],
        name=line_col,
        line=dict(color=CHART_PALETTE[1], width=2.5),
        mode="lines+markers",
        marker=dict(size=4),
        hovertemplate=f"<b>%{{x|%b %Y}}</b><br>{line_col}: %{{y:,.0f}}<extra></extra>",
    ), secondary_y=True)

    layout = get_plotly_layout(t)
    fig.update_layout(**layout, title=dict(
        text=f"📊 {bar_col} + {line_col} Combo",
        font=dict(color=t["text"], size=15), x=0, xanchor="left",
    ))
    return fig


def chart_growth_trend(df: pd.DataFrame, date_col: str, num_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    tmp = df[[date_col, num_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col])
    monthly = tmp.set_index(date_col).resample("ME")[num_col].sum()
    growth = monthly.pct_change() * 100

    colors_bar = [CHART_PALETTE[2] if v >= 0 else CHART_PALETTE[4] for v in growth.dropna()]
    fig = go.Figure(go.Bar(
        x=growth.dropna().index,
        y=growth.dropna().values,
        marker_color=colors_bar,
        text=[f"{v:+.1f}%" for v in growth.dropna().values],
        textposition="outside",
        textfont=dict(size=10, color=t["text2"]),
        hovertemplate="<b>%{x|%b %Y}</b><br>Growth: %{y:+.1f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=t["text2"], line_width=1, opacity=0.4)
    return apply_template(fig, f"📈 Monthly Growth Rate — {num_col}", t)


def chart_ranking(df: pd.DataFrame, cat_col: str, num_col: str, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    grp = df.groupby(cat_col, observed=True)[num_col].sum().nlargest(10).reset_index()
    grp = grp.sort_values(num_col)
    grp["rank"] = range(1, len(grp) + 1)
    colors_r = [CHART_PALETTE[4]] + [CHART_PALETTE[0]] * (len(grp) - 2) + [CHART_PALETTE[2]]

    fig = go.Figure(go.Bar(
        x=grp[num_col], y=grp[cat_col],
        orientation="h",
        marker_color=colors_r,
        text=[fmt_number(v) for v in grp[num_col]],
        textposition="outside",
        textfont=dict(size=11, color=t["text2"]),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    ))
    return apply_template(fig, f"🎖 Performance Ranking — {cat_col}", t)


def chart_correlation_heatmap(df: pd.DataFrame, num_cols: list, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    cols = num_cols[:8]
    corr = df[cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        color_continuous_scale=["#4f8ef7", t["card"], "#f87171"],
        zmin=-1, zmax=1,
    )
    fig.update_traces(hovertemplate="<b>%{x} × %{y}</b><br>r = %{z:.3f}<extra></extra>")
    return apply_template(fig, "🔗 Correlation Matrix", t)


def chart_top_n_analysis(df: pd.DataFrame, cat_col: str, num_col: str,
                          date_col: str = None, t: dict = None) -> go.Figure:
    if t is None:
        t = get_theme()
    top5 = df.groupby(cat_col, observed=True)[num_col].sum().nlargest(5).index.tolist()
    if date_col:
        tmp = df[df[cat_col].isin(top5)][[date_col, num_col, cat_col]].dropna().copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col])
        monthly_top = tmp.groupby([pd.Grouper(key=date_col, freq="ME"), cat_col])[num_col].sum().reset_index()
        fig = px.line(monthly_top, x=date_col, y=num_col, color=cat_col,
                      color_discrete_sequence=CHART_PALETTE)
        fig.update_traces(line_width=2)
        return apply_template(fig, f"🏅 Top 5 {cat_col} Trend", t)
    else:
        grp = df[df[cat_col].isin(top5)].groupby(cat_col, observed=True)[num_col].sum().reset_index()
        fig = px.bar(grp, x=cat_col, y=num_col, color=cat_col,
                     color_discrete_sequence=CHART_PALETTE)
        return apply_template(fig, f"🏅 Top 5 {cat_col}", t)


def chart_from_config(df: pd.DataFrame, chart_cfg: dict, schema: dict,
                       t: dict = None) -> go.Figure | None:
    if t is None:
        t = get_theme()
    chart_type = chart_cfg.get("type", "").lower()
    x = chart_cfg.get("x") or chart_cfg.get("x_axis")
    y = chart_cfg.get("y") or chart_cfg.get("y_axis")
    color = chart_cfg.get("color")
    title = chart_cfg.get("title", "")

    if x and x not in df.columns:
        x = None
    if y and y not in df.columns:
        y = None
    if color and color not in df.columns:
        color = None

    try:
        if chart_type == "bar" and x and y:
            grp = df.groupby(x, observed=True)[y].sum().nlargest(15).reset_index()
            fig = px.bar(grp, x=x, y=y, color_discrete_sequence=CHART_PALETTE)
            return apply_template(fig, title, t)
        elif chart_type == "line" and x and y:
            fig = px.line(df, x=x, y=y, color=color, color_discrete_sequence=CHART_PALETTE)
            return apply_template(fig, title, t)
        elif chart_type == "pie" and x:
            return chart_category_pie(df, x, y, t)
        elif chart_type == "scatter" and x and y:
            return chart_scatter(df, x, y, color, t)
        elif chart_type == "histogram" and x:
            return chart_distribution(df, x, t)
        elif chart_type == "heatmap" and schema.get("date") and y:
            return chart_monthly_heatmap(df, schema["date"][0], y, t)
        elif chart_type == "box" and x and y:
            return chart_box(df, x, y, t)
        elif chart_type == "treemap" and x and y:
            return chart_treemap(df, x, y, t)
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
        insights.append({"icon": "🏆", "title": "Top Performer",
                          "body": f"<strong>{top_name}</strong> leads with {fmt_number(top_val)} ({pct:.1f}% of total)."})
        bot_name = grp.idxmin()
        bot_val  = grp.min()
        insights.append({"icon": "⚠️", "title": "Needs Attention",
                          "body": f"<strong>{bot_name}</strong> has the lowest {primary} at {fmt_number(bot_val)}."})

    if primary and schema["date"] and len(insights) < 6:
        dcol = schema["date"][0]
        tmp = df[[dcol, primary]].dropna().copy()
        tmp[dcol] = pd.to_datetime(tmp[dcol])
        monthly = tmp.set_index(dcol).resample("ME")[primary].sum()
        if len(monthly) >= 2:
            peak_m = monthly.idxmax()
            insights.append({"icon": "📈", "title": "Peak Period",
                              "body": f"Highest {primary} in <strong>{peak_m.strftime('%B %Y')}</strong> at {fmt_number(monthly.max())}."})
            last2 = monthly.iloc[-2:]
            if len(last2) == 2:
                chg = (last2.iloc[-1] - last2.iloc[-2]) / (abs(last2.iloc[-2]) + 1e-9) * 100
                arrow = "↑" if chg >= 0 else "↓"
                insights.append({"icon": "📊", "title": "Recent Trend",
                                  "body": f"Last month changed <strong>{arrow} {abs(chg):.1f}%</strong> vs the previous month."})

    if primary and len(insights) < 7:
        z = (df[primary] - df[primary].mean()) / (df[primary].std() + 1e-9)
        outlier_count = (z.abs() > 3).sum()
        if outlier_count > 0:
            insights.append({"icon": "🔍", "title": "Outliers Detected",
                              "body": f"<strong>{outlier_count}</strong> records fall outside 3 standard deviations of {primary}."})

    if len(num_cols) >= 2 and len(insights) < 8:
        try:
            corr = df[num_cols].corr()
            np.fill_diagonal(corr.values, 0)
            max_corr = corr.abs().unstack().idxmax()
            c1, c2 = max_corr
            if c1 != c2:
                r = corr.loc[c1, c2]
                direction = "positive" if r > 0 else "negative"
                insights.append({"icon": "🔗", "title": "Correlation Found",
                                  "body": f"Strong {direction} correlation (r={r:.2f}) between <strong>{c1}</strong> and <strong>{c2}</strong>."})
        except Exception:
            pass

    if not insights:
        insights.append({"icon": "📋", "title": "Dataset Loaded",
                          "body": f"Dataset has <strong>{len(df):,}</strong> rows and <strong>{len(df.columns)}</strong> columns ready for analysis."})

    return insights[:8]


# ─────────────────────────────────────────────
# TOP / BOTTOM ANALYSIS
# ─────────────────────────────────────────────
def render_top_bottom(df: pd.DataFrame, cat_col: str, num_col: str, n: int = 5):
    t = get_theme()
    grp = df.groupby(cat_col, observed=True)[num_col].sum()
    total = grp.sum()
    top_n = grp.nlargest(n)
    bot_n = grp.nsmallest(n)

    c1, c2 = st.columns(2)
    with c1:
        html = f"""
        <div class="glass-card">
            <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.09em;color:{t['accent3']};margin-bottom:0.9rem;">
                🏆 Top {n} — {cat_col}
            </div>
            <table class="rank-table">
                <tr><th>#</th><th>{cat_col}</th><th>{num_col}</th><th>Share</th></tr>"""
        for i, (name, val) in enumerate(top_n.items()):
            pct = val / total * 100 if total else 0
            html += f"""
                <tr>
                    <td class="rank-num">{i+1}</td>
                    <td>{name}</td>
                    <td class="rank-val">{fmt_number(val)}</td>
                    <td><span class="rank-badge top">{pct:.1f}%</span></td>
                </tr>"""
        html += "</table></div>"
        st.markdown(html, unsafe_allow_html=True)

    with c2:
        html = f"""
        <div class="glass-card">
            <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.09em;color:{t['danger']};margin-bottom:0.9rem;">
                ⚠️ Bottom {n} — {cat_col}
            </div>
            <table class="rank-table">
                <tr><th>#</th><th>{cat_col}</th><th>{num_col}</th><th>Share</th></tr>"""
        for i, (name, val) in enumerate(bot_n.items()):
            pct = val / total * 100 if total else 0
            html += f"""
                <tr>
                    <td class="rank-num">{i+1}</td>
                    <td>{name}</td>
                    <td class="rank-val">{fmt_number(val)}</td>
                    <td><span class="rank-badge bot">{pct:.1f}%</span></td>
                </tr>"""
        html += "</table></div>"
        st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TIME COMPARISON DISPLAY
# ─────────────────────────────────────────────
def render_time_comparisons(time_comps: dict):
    if not time_comps:
        return
    t = get_theme()
    cards = []
    for key in ["mom", "qoq", "yoy"]:
        if key in time_comps:
            tc = time_comps[key]
            val = tc["value"]
            cls = "pos" if val >= 0 else "neg"
            arrow = "↑" if val >= 0 else "↓"
            cards.append({
                "label": tc["label"],
                "value": f"{arrow} {abs(val):.1f}%",
                "cls": cls,
                "period": tc.get("period", ""),
            })
    for key in ["best_period", "worst_period"]:
        if key in time_comps:
            tc = time_comps[key]
            cards.append({
                "label": tc["label"],
                "value": fmt_number(tc["value"]),
                "cls": "pos" if key == "best_period" else "neg",
                "period": tc.get("period", ""),
            })

    html = '<div class="comparison-grid">'
    for card in cards:
        html += f"""
        <div class="comparison-card">
            <div class="comparison-label">{card["label"]}</div>
            <div class="comparison-value {card["cls"]}">{card["value"]}</div>
            <div style="font-size:0.74rem;color:{t['muted']};margin-top:4px">{card["period"]}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
def render_sidebar_filters(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    t = get_theme()
    muted_color = t["muted"]
    st.sidebar.markdown(
        f"<div style='font-size:0.85rem;font-weight:700;text-transform:uppercase;"
        f"letter-spacing:0.08em;color:{muted_color};margin-bottom:0.8rem;margin-top:0.5rem'>⚙ Filters</div>",
        unsafe_allow_html=True,
    )

    filtered = df.copy()
    active_filters = []

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
                if sel[0] != mn or sel[1] != mx:
                    active_filters.append(f"📅 {sel[0]} → {sel[1]}")

    shown = 0
    for col in schema["categorical"]:
        if shown >= 5:
            break
        vals = sorted(df[col].dropna().unique().tolist())
        if 1 < len(vals) <= 100:
            sel = st.sidebar.multiselect(col, vals, default=[], key=f"filter_{col}")
            if sel:
                filtered = filtered[filtered[col].isin(sel)]
                active_filters.append(f"🏷 {col}: {', '.join(str(s) for s in sel[:2])}{'…' if len(sel)>2 else ''}")
            shown += 1

    if schema["numeric"]:
        num_col = schema["numeric"][0]
        col_data = df[num_col].dropna()
        if not col_data.empty:
            mn, mx = float(col_data.min()), float(col_data.max())
            if mn < mx:
                sel = st.sidebar.slider(f"{num_col} Range", mn, mx, (mn, mx), key=f"slider_{num_col}")
                filtered = filtered[(filtered[num_col] >= sel[0]) & (filtered[num_col] <= sel[1])]
                if sel[0] != mn or sel[1] != mx:
                    active_filters.append(f"🔢 {num_col}: {fmt_number(sel[0])}–{fmt_number(sel[1])}")

    # Reset button
    if active_filters:
        if st.sidebar.button("✕ Reset Filters", use_container_width=True, key="reset_filters"):
            for key in list(st.session_state.keys()):
                if key.startswith("filter_") or key in ("date_range",) or key.startswith("slider_"):
                    del st.session_state[key]
            st.rerun()

    st.sidebar.markdown("---")

    # Row count
    pct_shown = len(filtered) / len(df) * 100 if len(df) > 0 else 100
    st.sidebar.markdown(
        f"<div style='font-size:0.82rem;color:{t['muted']};margin-bottom:4px'>"
        f"Showing <strong style='color:{t['text']}'>{len(filtered):,}</strong> of {len(df):,} rows "
        f"<span style='color:{t['accent1']}'>({pct_shown:.0f}%)</span></div>",
        unsafe_allow_html=True,
    )

    # Active filters summary
    if active_filters:
        summary = " · ".join(active_filters[:3])
        st.sidebar.markdown(
            f"<div class='filter-summary'>{len(active_filters)} filter{'s' if len(active_filters)>1 else ''} active · {summary}</div>",
            unsafe_allow_html=True,
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
# AI INSIGHTS PAGE
# ─────────────────────────────────────────────
def render_ai_insights_page(df: pd.DataFrame, schema: dict, primary: str | None,
                              config: dict, time_comps: dict, file_label: str):
    t = get_theme()

    st.markdown(f"""
    <div style='padding:.5rem 0 1.5rem'>
        <div class='dash-title' style='font-size:2rem'>{file_label} · AI Insights</div>
        <div class='dash-sub'>Intelligent analysis, recommendations, and strategic opportunities</div>
    </div>
    """, unsafe_allow_html=True)

    cat_cols = schema["categorical"]
    num_cols = schema["numeric"]

    def ai_section(icon: str, label: str, content: str, items: list = None):
        items_html = ""
        if items:
            items_html = "<ul class='ai-list'>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"
        st.markdown(f"""
        <div class="ai-section">
            <div class="ai-section-label">{icon} {label}</div>
            <div class="ai-section-content">{content}{items_html}</div>
        </div>""", unsafe_allow_html=True)

    # ── 1. Executive Summary ──
    summary_text = (config.get("summary") if config else None) or \
                   generate_executive_summary(df, schema, primary, config, file_label)
    ai_section("📋", "Executive Summary", summary_text)

    # ── 2. Key Findings ──
    findings = []
    if config and config.get("insights"):
        findings = [ins.get("body", ins.get("text", "")) for ins in config["insights"][:5]]
    if not findings and primary:
        grp = df.groupby(cat_cols[0], observed=True)[primary].sum() if cat_cols else None
        if grp is not None:
            findings.append(f"<strong>{grp.idxmax()}</strong> is the top-performing {cat_cols[0]} with {fmt_number(grp.max())} total {primary}.")
            findings.append(f"The bottom 20% of {cat_cols[0]} segments account for less than {fmt_number(grp.nsmallest(max(1,len(grp)//5)).sum())} combined.")
        if time_comps and "yoy" in time_comps:
            yoy = time_comps["yoy"]
            findings.append(f"Year-over-year performance shows a <strong>{yoy['value']:+.1f}%</strong> change ({yoy['period']}).")
    ai_section("🔍", "Key Findings", "Based on the dataset analysis:", findings or ["Insufficient data for automatic findings."])

    # ── 3. Opportunities ──
    opps = []
    if config and config.get("opportunities"):
        opps = config["opportunities"] if isinstance(config["opportunities"], list) else [config["opportunities"]]
    if not opps and cat_cols and primary:
        grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
        avg = grp.mean()
        below_avg = grp[grp < avg].index.tolist()
        if below_avg:
            opps.append(f"<strong>{len(below_avg)} segments</strong> are below the average {primary}. Targeted investment could lift overall performance.")
        if len(num_cols) >= 2:
            opps.append(f"Cross-sell potential exists between <strong>{num_cols[0]}</strong> and <strong>{num_cols[1]}</strong> — explore bundling strategies.")
        opps.append("Automating reporting on low-performing segments may surface actionable patterns faster.")
    ai_section("🚀", "Opportunities", "Growth and improvement areas identified:", opps or ["No specific opportunities detected."])

    # ── 4. Risks ──
    risks = []
    if config and config.get("risks"):
        risks = config["risks"] if isinstance(config["risks"], list) else [config["risks"]]
    if not risks and primary:
        z = (df[primary] - df[primary].mean()) / (df[primary].std() + 1e-9)
        outliers = (z.abs() > 3).sum()
        if outliers > 0:
            risks.append(f"<strong>{outliers} outlier records</strong> detected in {primary} — may indicate data quality issues or unusual events.")
        if cat_cols:
            grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
            concentration = grp.max() / grp.sum() * 100
            if concentration > 40:
                risks.append(f"High concentration risk: <strong>{grp.idxmax()}</strong> represents {concentration:.1f}% of total {primary}.")
        risks.append("Seasonal or temporal fluctuations may affect forecast accuracy — validate against external benchmarks.")
    ai_section("⚠️", "Risks", "Potential risks and concerns to monitor:", risks or ["No specific risks detected."])

    # ── 5. Trends ──
    trends = []
    if config and config.get("trends"):
        trends = config["trends"] if isinstance(config["trends"], list) else [config["trends"]]
    if not trends and schema["date"] and primary:
        try:
            tmp = df[[schema["date"][0], primary]].dropna().copy()
            tmp[schema["date"][0]] = pd.to_datetime(tmp[schema["date"][0]])
            monthly = tmp.set_index(schema["date"][0]).resample("ME")[primary].sum()
            if len(monthly) >= 3:
                recent3 = monthly.iloc[-3:]
                if recent3.is_monotonic_increasing:
                    trends.append(f"<strong>Positive momentum:</strong> {primary} has increased for 3 consecutive months.")
                elif recent3.is_monotonic_decreasing:
                    trends.append(f"<strong>Declining trend:</strong> {primary} has decreased for 3 consecutive months — investigate root causes.")
                overall_growth = (monthly.iloc[-1] - monthly.iloc[0]) / (abs(monthly.iloc[0]) + 1e-9) * 100
                trends.append(f"Overall trend shows <strong>{overall_growth:+.1f}%</strong> change from {monthly.index[0].strftime('%b %Y')} to {monthly.index[-1].strftime('%b %Y')}.")
        except Exception:
            pass
    ai_section("📈", "Trends", "Key patterns and directional signals:", trends or ["Insufficient time-series data for trend analysis."])

    # ── 6. Recommendations ──
    recs = []
    if config and config.get("recommendations"):
        recs = config["recommendations"] if isinstance(config["recommendations"], list) else [config["recommendations"]]
    if not recs:
        if primary and cat_cols:
            grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
            recs.append(f"Prioritize resources toward <strong>{grp.idxmax()}</strong> — the highest-value {cat_cols[0]} segment.")
            recs.append(f"Investigate <strong>{grp.idxmin()}</strong> for potential turnaround or resource reallocation.")
        recs.append("Establish weekly KPI reviews to track momentum and catch early signals of performance shifts.")
        recs.append("Consider segmenting the dataset further by secondary dimensions to unlock deeper insights.")
    ai_section("💡", "Recommendations", "Strategic actions based on the analysis:", recs)

    # ── 7. Anomalies ──
    anomalies = []
    if config and config.get("anomalies"):
        anomalies = config["anomalies"] if isinstance(config["anomalies"], list) else [config["anomalies"]]
    if not anomalies and primary:
        z = (df[primary] - df[primary].mean()) / (df[primary].std() + 1e-9)
        top_outliers = df[z.abs() > 2.5][primary].nlargest(3)
        for val in top_outliers:
            anomalies.append(f"Extreme value detected: <strong>{fmt_number(val)}</strong> in {primary} (z > 2.5σ).")
        if not anomalies:
            anomalies.append("No significant anomalies detected. Data distribution appears within normal ranges.")
    ai_section("🔬", "Anomalies", "Unusual patterns or values detected:", anomalies)

    # ── 8. Top Drivers ──
    drivers = []
    if config and config.get("drivers"):
        drivers = config["drivers"] if isinstance(config["drivers"], list) else [config["drivers"]]
    if not drivers and primary and num_cols:
        try:
            corrs = df[num_cols].corr()[primary].drop(primary).abs().sort_values(ascending=False)
            for col, r in corrs.head(3).items():
                strength = "strong" if r > 0.7 else "moderate" if r > 0.4 else "weak"
                drivers.append(f"<strong>{col}</strong> shows a {strength} correlation (r={r:.2f}) with {primary}.")
        except Exception:
            pass
        if cat_cols:
            grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
            top_cat = grp.idxmax()
            drivers.append(f"Segment <strong>{top_cat}</strong> is a primary driver of {primary} performance.")
    ai_section("🎯", "Top Drivers", "Key factors influencing performance:", drivers or ["Correlation analysis requires numeric columns."])

    # ── 9-12. Growth, Performance, Category, Forecast ──
    c1, c2 = st.columns(2)
    with c1:
        if schema["date"] and primary:
            try:
                tmp = df[[schema["date"][0], primary]].dropna().copy()
                tmp[schema["date"][0]] = pd.to_datetime(tmp[schema["date"][0]])
                monthly = tmp.set_index(schema["date"][0]).resample("ME")[primary].sum()
                quarterly = tmp.set_index(schema["date"][0]).resample("QE")[primary].sum()
                items = []
                if len(monthly) >= 2:
                    best_m = monthly.idxmax()
                    items.append(f"Best month: <strong>{best_m.strftime('%B %Y')}</strong> ({fmt_number(monthly.max())})")
                if len(quarterly) >= 2:
                    best_q = quarterly.idxmax()
                    items.append(f"Best quarter: <strong>Q{best_q.quarter} {best_q.year}</strong> ({fmt_number(quarterly.max())})")
                ai_section("📊", "Growth Analysis", "Period-over-period growth highlights:", items)
            except Exception:
                pass

    with c2:
        if primary and cat_cols:
            grp = df.groupby(cat_cols[0], observed=True)[primary].sum()
            mean_v = grp.mean()
            above = (grp >= mean_v).sum()
            below = (grp < mean_v).sum()
            items = [
                f"<strong>{above}</strong> segments at or above average performance",
                f"<strong>{below}</strong> segments below average — review required",
                f"Average {primary} per segment: <strong>{fmt_number(mean_v)}</strong>",
                f"Performance spread: {fmt_number(grp.max() - grp.min())} range",
            ]
            ai_section("⚡", "Performance Analysis", "Segment performance distribution:", items)


# ─────────────────────────────────────────────
# RENDER DASHBOARD (core logic)
# ─────────────────────────────────────────────
def render_dashboard(df_raw: pd.DataFrame, file_label: str, config: dict = None,
                     dashboard_meta: dict = None):
    """Main dashboard rendering – call with loaded dataframe + optional config."""
    t = get_theme()

    schema  = detect_schema(df_raw)
    df_raw  = coerce_dates(df_raw, schema["date"])
    primary = pick_primary_measure(df_raw, schema["numeric"], config)

    # Sidebar filters
    df = render_sidebar_filters(df_raw, schema)

    # ── Sidebar branding & expiry ──
    with st.sidebar:
        if dashboard_meta:
            expires = dashboard_meta.get("expires_at", "")
            if expires:
                try:
                    exp = datetime.fromisoformat(expires.replace("Z", ""))
                    days_left = (exp - datetime.now()).days
                    color = t["success"] if days_left > 5 else t["accent4"] if days_left > 1 else t["danger"]
                    st.markdown(
                        f"<div style='font-size:0.78rem;color:{color};margin-top:8px;padding:6px 10px;"
                        f"background:rgba(52,211,153,0.08);border-radius:8px;border:1px solid {color}40'>"
                        f"⏱ Expires in {days_left} day{'s' if days_left != 1 else ''}</div>",
                        unsafe_allow_html=True,
                    )
                except Exception:
                    pass

    # ── Time comparisons ──
    time_comps = {}
    if schema["date"] and primary:
        time_comps = compute_time_comparisons(df, schema["date"][0], primary)

    # ── MULTI-PAGE TABS ──
    tab1, tab2 = st.tabs(["📊  Executive Dashboard", "🤖  AI Insights"])

    # ══════════════════════════════════
    # TAB 1: EXECUTIVE DASHBOARD
    # ══════════════════════════════════
    with tab1:
        # ── Header ──
        dataset_type = config.get("dataset_type", "") if config else ""
        type_badge = f" · {dataset_type.upper()}" if dataset_type else ""
        st.markdown(f"""
        <div style='padding:.5rem 0 1rem'>
            <div class='dash-title'>{file_label}{type_badge}</div>
            <div class='dash-sub'>Automatically generated enterprise analytics dashboard · {datetime.now().strftime("%B %d, %Y")}</div>
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

        # ── Executive Summary ──
        summary_text = generate_executive_summary(df, schema, primary, config, file_label)
        st.markdown(f"""
        <div class="exec-summary">
            <div class="exec-summary-label">✦ Executive Summary</div>
            <div class="exec-summary-body">{summary_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPIs ──
        section_header("Key Performance Indicators", "KPIs")
        kpis = build_kpis(df, schema, primary, config, time_comps)
        render_kpi_cards(kpis)

        # ── Time Comparisons ──
        if time_comps:
            section_header("Period Comparisons", "Time Analysis")
            render_time_comparisons(time_comps)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # ── CHARTS ──
        has_date = bool(schema["date"])
        has_num  = bool(schema["numeric"])
        has_cat  = bool(schema["categorical"])
        rendered = 0

        section_header("Visualizations",
                       "AI-selected" if config and config.get("recommended_charts") else "Auto-selected")

        # If Gemini provided chart config, render those first
        if config and config.get("recommended_charts"):
            charts_from_config = []
            for ch in config["recommended_charts"]:
                fig = chart_from_config(df, ch, schema, t)
                if fig:
                    charts_from_config.append(fig)

            for i in range(0, len(charts_from_config), 2):
                if i + 1 < len(charts_from_config):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.plotly_chart(charts_from_config[i],   use_container_width=True)
                    with c2:
                        st.plotly_chart(charts_from_config[i+1], use_container_width=True)
                else:
                    st.plotly_chart(charts_from_config[i], use_container_width=True)
                rendered += 1

        # Auto charts (fill in gaps / fallback)
        if rendered == 0:
            if has_date and primary:
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.plotly_chart(chart_time_series(df, schema["date"][0], primary, t),
                                    use_container_width=True)
                with c2:
                    if has_cat:
                        st.plotly_chart(chart_category_pie(df, schema["categorical"][0], primary, t),
                                        use_container_width=True)
                    else:
                        st.plotly_chart(chart_distribution(df, primary, t), use_container_width=True)
                rendered += 1

            if has_cat and primary:
                c1, c2 = st.columns(2)
                with c1:
                    st.plotly_chart(chart_category_bar(df, schema["categorical"][0], primary, t=t),
                                    use_container_width=True)
                with c2:
                    st.plotly_chart(chart_treemap(df, schema["categorical"][0], primary, t),
                                    use_container_width=True)
                rendered += 1

            if has_date and primary:
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.plotly_chart(chart_growth_trend(df, schema["date"][0], primary, t),
                                    use_container_width=True)
                with c2:
                    st.plotly_chart(chart_monthly_heatmap(df, schema["date"][0], primary, t),
                                    use_container_width=True)
                rendered += 1

            if has_cat and primary and has_date:
                st.plotly_chart(
                    chart_top_n_analysis(df, schema["categorical"][0], primary, schema["date"][0], t),
                    use_container_width=True,
                )
                rendered += 1

            if len(schema["numeric"]) >= 2:
                c1, c2 = st.columns(2)
                with c1:
                    color_col = schema["categorical"][0] if has_cat else None
                    st.plotly_chart(chart_scatter(df, schema["numeric"][0],
                                                  schema["numeric"][1], color_col, t),
                                    use_container_width=True)
                with c2:
                    if has_cat and primary:
                        st.plotly_chart(chart_box(df, schema["categorical"][0], primary, t),
                                        use_container_width=True)
                    else:
                        st.plotly_chart(chart_distribution(df, schema["numeric"][1], t),
                                        use_container_width=True)
                rendered += 1

            if len(schema["numeric"]) >= 2:
                st.plotly_chart(chart_correlation_heatmap(df, schema["numeric"], t),
                                use_container_width=True)
                rendered += 1

            if has_date and len(schema["numeric"]) >= 2:
                st.plotly_chart(
                    chart_combo(df, schema["date"][0], schema["numeric"][0], schema["numeric"][1], t),
                    use_container_width=True,
                )
                rendered += 1

            if rendered == 0:
                if has_num:
                    st.plotly_chart(chart_distribution(df, schema["numeric"][0], t),
                                    use_container_width=True)
                elif has_cat:
                    st.plotly_chart(chart_cat_count(df, schema["categorical"][0], t),
                                    use_container_width=True)
                else:
                    st.info("No plottable columns found. Check your dataset.")

        # ── TOP / BOTTOM ANALYSIS ──
        if has_cat and primary:
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            section_header("Performance Ranking", "Top vs Bottom")
            render_top_bottom(df, schema["categorical"][0], primary)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # ── INSIGHTS ──
        section_header("Automated Insights",
                       "Gemini AI" if config and config.get("insights") else "Auto-detected")
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

    # ══════════════════════════════════
    # TAB 2: AI INSIGHTS
    # ══════════════════════════════════
    with tab2:
        render_ai_insights_page(df, schema, primary, config or {}, time_comps, file_label)


# ─────────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────────
def render_welcome():
    t = get_theme()
    st.markdown(f"""
    <div style='padding:2rem 0 1rem'>
        <div class='dash-title'>Analytics Platform</div>
        <div class='dash-sub' style='font-size:1.05rem'>Drop any CSV or Excel file — instant enterprise analytics.</div>
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
    # ── Session state defaults ──
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True

    # ── Inject CSS ──
    t = get_theme()
    inject_css(t)

    # ── Get dashboard ID from URL params ──
    query_params = st.query_params
    dashboard_id = query_params.get("dashboard") or query_params.get("id")

    # ── Sidebar branding + theme toggle ──
    with st.sidebar:
        st.markdown(f"""
        <div style='margin-bottom:1.2rem;padding-bottom:1rem;border-bottom:1px solid {t["border2"]}'>
            <div style='font-size:1.2rem;font-weight:800;
                        background:linear-gradient(120deg,{t["accent1"]},{t["accent2"]});
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text'>
                📊 Analytics
            </div>
            <div style='font-size:0.75rem;color:{t["muted"]};margin-top:2px;font-weight:500'>
                Enterprise Dashboard Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Theme toggle
        dark_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
        if st.button(dark_label, use_container_width=True, key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown("<div style='margin-bottom:0.8rem'></div>", unsafe_allow_html=True)

        # Manual upload (dev/testing mode only when no dashboard_id)
        if not dashboard_id:
            uploaded = st.file_uploader(
                "Upload Dataset",
                type=["csv", "xlsx", "xls"],
                label_visibility="collapsed",
            )
        else:
            uploaded = None

    # ══════════════════════════════════
    # MODE 1: URL-based (Telegram flow)
    # ══════════════════════════════════
    if dashboard_id:
        if check_dashboard_expired(dashboard_id):
            st.markdown("""
            <div class='expired-banner'>
                <div style='font-size:3rem;margin-bottom:1rem'>⏰</div>
                <div style='font-size:1.4rem;font-weight:800;color:#f87171'>Dashboard Expired</div>
                <div style='color:#64748b;margin-top:.6rem;font-size:0.95rem'>
                    This dashboard was available for 15 days and has now expired.<br>
                    Please upload a new file via the Telegram bot.
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        with st.spinner("Loading dashboard…"):
            meta = get_dashboard_meta(dashboard_id)

        if not meta:
            st.error("❌ Dashboard not found. It may have been deleted or the link is invalid.")
            return

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

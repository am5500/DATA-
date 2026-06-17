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
import hashlib
import datetime
import uuid as _uuid
import json as _json
import base64 as _b64
import re as _re

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
    --font-scale: 1;
}

/* ── Display modes ── */
body.mode-compact { --font-scale: 0.88; }
body.mode-large   { --font-scale: 1.13; }

/* ── Base ── */
html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text);
    font-size: calc(15px * var(--font-scale));
    scroll-behavior: smooth;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
    transition: width .35s cubic-bezier(.4,0,.2,1), transform .35s cubic-bezier(.4,0,.2,1);
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

/* ── Sidebar collapse button (Streamlit native) ── */
[data-testid="collapsedControl"] {
    background: var(--card2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 0 10px 10px 0 !important;
    color: var(--accent1) !important;
    transition: background .2s, box-shadow .2s;
    box-shadow: 2px 0 12px rgba(0,0,0,0.4);
}
[data-testid="collapsedControl"]:hover {
    background: rgba(79,142,247,0.15) !important;
    box-shadow: 2px 0 20px rgba(79,142,247,0.2);
}

/* ── Hide default header ── */
header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── Sticky dashboard header ── */
.sticky-header {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(8,10,15,0.92);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    padding: .75rem 0 .6rem;
    margin: 0 -1rem;
    padding-left: 1rem;
    padding-right: 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}

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
   KPI CARDS — Premium Glassmorphism (unchanged)
══════════════════════════════════════════ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 2.5rem;
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
    padding: 3px 9px;
    border-radius: 99px;
    letter-spacing: .02em;
    display: inline-flex;
    align-items: center;
    gap: 3px;
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
    font-size: calc(2.1rem * var(--font-scale));
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

/* ── KPI animated counter ── */
@keyframes countUp {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
.kpi-value { animation: countUp .5s ease both; }
.kpi-card:nth-child(2) .kpi-value { animation-delay: .05s; }
.kpi-card:nth-child(3) .kpi-value { animation-delay: .10s; }
.kpi-card:nth-child(4) .kpi-value { animation-delay: .15s; }
.kpi-card:nth-child(5) .kpi-value { animation-delay: .20s; }
.kpi-card:nth-child(6) .kpi-value { animation-delay: .25s; }
.kpi-card:nth-child(7) .kpi-value { animation-delay: .30s; }
.kpi-card:nth-child(8) .kpi-value { animation-delay: .35s; }

/* ══════════════════════════════════════════
   SECTION HEADERS — enhanced
══════════════════════════════════════════ */
.section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2.8rem 0 1.4rem;
    position: relative;
}
.section-head::before {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 40px;
    height: 2px;
    background: var(--accent1);
    border-radius: 99px;
    opacity: 0.6;
}
.section-head-icon {
    font-size: 1.2rem;
    line-height: 1;
}
.section-head h2 {
    font-size: calc(1.25rem * var(--font-scale));
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

/* ── Section separator — richer ── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 3rem 0;
    position: relative;
}
.divider::after {
    content: '';
    position: absolute;
    top: -1px; left: 0;
    width: 80px; height: 1px;
    background: linear-gradient(90deg, rgba(79,142,247,0.5), transparent);
}

/* ══════════════════════════════════════════
   DASHBOARD TITLE
══════════════════════════════════════════ */
.dash-title {
    font-size: calc(2.2rem * var(--font-scale));
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

/* ── Dashboard header badges ── */
.header-badges-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: .65rem;
}
.hbadge {
    font-size: .68rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 99px;
    background: rgba(79,142,247,0.08);
    border: 1px solid rgba(79,142,247,0.18);
    color: var(--accent1);
    letter-spacing: .03em;
}
.hbadge-green {
    background: rgba(52,211,153,0.08);
    border-color: rgba(52,211,153,0.2);
    color: #34d399;
}
.hbadge-purple {
    background: rgba(167,139,250,0.08);
    border-color: rgba(167,139,250,0.2);
    color: var(--accent2);
}
.hbadge-amber {
    background: rgba(245,158,11,0.08);
    border-color: rgba(245,158,11,0.2);
    color: var(--accent4);
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

/* ── Dashboard metadata card ── */
.meta-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
    margin-top: 1rem;
}
.meta-info-item {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: .8rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.meta-info-label {
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--muted);
}
.meta-info-value {
    font-size: .92rem;
    font-weight: 600;
    color: var(--text2);
    font-family: 'DM Mono', monospace;
}

/* ── Insight cards — enhanced ── */
.insight-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 14px;
}
.insight-card {
    background: var(--card2);
    border: 1px solid var(--border2);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    display: flex;
    gap: 14px;
    align-items: flex-start;
    box-shadow: var(--shadow-sm);
    transition: border-color .25s, transform .25s, box-shadow .25s;
    position: relative;
    overflow: hidden;
}
.insight-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent2);
    opacity: 0.5;
}
.insight-card:hover {
    border-color: rgba(167,139,250,0.35);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4), 0 0 20px rgba(167,139,250,0.08);
}
.insight-icon {
    font-size: 1.8rem;
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
.insight-value-highlight {
    font-family: 'DM Mono', monospace;
    font-weight: 700;
    color: var(--accent1);
    font-size: 1rem;
    display: block;
    margin-top: 4px;
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
/* Tabs — enhanced */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important;
    border-radius: var(--radius-sm) !important;
    padding: 5px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 7px 20px !important;
    transition: background .2s, color .2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(79,142,247,0.08) !important;
    color: var(--text2) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(79,142,247,0.18) !important;
    color: var(--accent1) !important;
    box-shadow: 0 0 0 1px rgba(79,142,247,0.25) !important;
}

/* ── Data table search bar ── */
.data-search-bar {
    background: var(--card2);
    border: 1px solid var(--border2);
    border-radius: 10px;
    padding: .5rem 1rem;
    color: var(--text);
    font-size: 14px;
    width: 100%;
    margin-bottom: .75rem;
    outline: none;
    transition: border-color .2s;
    font-family: 'Inter', sans-serif;
}
.data-search-bar:focus { border-color: rgba(79,142,247,0.5); }

/* ── Column stats bar ── */
.col-stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 8px;
    margin-bottom: 1rem;
}
.col-stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .6rem .9rem;
}
.col-stat-name {
    font-size: .65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: var(--muted);
    margin-bottom: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.col-stat-val {
    font-size: .88rem;
    font-weight: 600;
    color: var(--text2);
    font-family: 'DM Mono', monospace;
}

/* ── Pagination ── */
.pagination-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: .75rem;
    font-size: .82rem;
    color: var(--muted);
}
.pagination-btns { display: flex; gap: 6px; }
.pag-btn {
    background: var(--card2);
    border: 1px solid var(--border2);
    border-radius: 8px;
    color: var(--text2);
    font-size: .8rem;
    font-weight: 600;
    padding: 4px 12px;
    cursor: pointer;
    transition: background .15s, border-color .15s;
}
.pag-btn:hover { background: rgba(79,142,247,0.15); border-color: rgba(79,142,247,0.35); }
.pag-btn.active { background: rgba(79,142,247,0.2); border-color: #4f8ef7; color: #4f8ef7; }
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
            font=dict(color="#e8edf5", size=17, family="Inter", weight=700),
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


def fmt_number(n, is_percent=False) -> str:
    """Smart number formatting, with optional percent."""
    if pd.isna(n):
        return "—"
    if is_percent:
        return f"{n:.1f}%"
    n = float(n)
    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
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


def chart_grouped_bar(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None) -> go.Figure:
    """Grouped bar chart comparing x_col vs y_col by color_col (if provided)."""
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


def chart_pareto(df: pd.DataFrame, cat_col: str, num_col: str) -> go.Figure:
    """Pareto chart with secondary y-axis using make_subplots."""
    grp = df.groupby(cat_col, observed=True)[num_col].sum().sort_values(ascending=False).head(15).reset_index()
    grp["cumulative_pct"] = grp[num_col].cumsum() / grp[num_col].sum() * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(go.Bar(
        x=grp[cat_col], y=grp[num_col], name=num_col,
        marker_color=CHART_PALETTE[0],
        marker_line_width=0,
        text=grp[num_col],
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Value: <b>%{y:,.0f}</b><extra></extra>",
    ), secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x=grp[cat_col], y=grp["cumulative_pct"],
        name="Cumulative %",
        line=dict(color=CHART_PALETTE[3], width=2.5),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Cumulative: <b>%{y:.1f}%</b><extra></extra>",
    ), secondary_y=True)
    
    fig.update_layout(
        xaxis_tickangle=-30,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(
        title_text=num_col,
        secondary_y=False,
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=12),
        title_font=dict(size=13),
    )
    fig.update_yaxes(
        title_text="Cumulative %",
        secondary_y=True,
        ticksuffix="%",
        range=[0, 110],
        showgrid=False,
        titlefont=dict(color=CHART_PALETTE[3], size=12),
        tickfont=dict(color=CHART_PALETTE[3]),
    )
    return apply_template(fig, f"📊 Pareto: {num_col} by {cat_col}")


def chart_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None) -> go.Figure:
    """Scatter plot for numeric columns."""
    if color_col and df[color_col].nunique() <= 12:
        fig = px.scatter(df.sample(min(1000, len(df))), x=x_col, y=y_col, color=color_col,
                         color_discrete_sequence=CHART_PALETTE,
                         hover_data=[x_col, y_col, color_col])
    else:
        fig = px.scatter(df.sample(min(1000, len(df))), x=x_col, y=y_col,
                         color_discrete_sequence=[CHART_PALETTE[0]])
    fig.update_traces(marker=dict(size=5, opacity=0.6))
    return apply_template(fig, f"🔵 {x_col} vs {y_col}")


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


# ─────────────────────────────────────────────
# INSIGHTS (Single unified version)
# ─────────────────────────────────────────────
def generate_insights(df: pd.DataFrame, schema: dict, primary: str | None) -> list[dict]:
    """Generate automated insight cards from the dataset."""
    insights = []
    colors = CHART_PALETTE

    # 1. Best category
    if primary and schema["categorical"]:
        cat_col = schema["categorical"][0]
        grp = df.groupby(cat_col, observed=True)[primary].sum()
        best = grp.idxmax()
        insights.append({
            "icon": "🏆",
            "title": "Best Category",
            "body": f"<b>{best}</b> leads in <b>{primary}</b> with the highest total.",
            "highlight": fmt_number(grp[best]),
        })
        # Worst category
        worst = grp.idxmin()
        insights.append({
            "icon": "📉",
            "title": "Lowest Performance",
            "body": f"<b>{worst}</b> has the lowest total <b>{primary}</b>.",
            "highlight": fmt_number(grp[worst]),
        })

    # 2. Growth trend
    if primary and schema["date"]:
        dcol = schema["date"][0]
        try:
            tmp = df[[dcol, primary]].dropna()
            tmp[dcol] = pd.to_datetime(tmp[dcol])
            monthly = tmp.set_index(dcol).resample("ME")[primary].sum()
            if len(monthly) >= 3:
                recent   = monthly.iloc[-1]
                previous = monthly.iloc[-2]
                pct = (recent - previous) / (abs(previous) + 1e-9) * 100
                direction = "grew" if pct >= 0 else "fell"
                emoji = "📈" if pct >= 0 else "📉"
                insights.append({
                    "icon": emoji,
                    "title": "Recent Trend",
                    "body": f"{primary} {direction} <b>{abs(pct):.1f}%</b> last month ({monthly.index[-1].strftime('%b %Y')}).",
                    "highlight": fmt_number(recent),
                })
        except Exception:
            pass

    # 3. Anomaly detection (simple z-score)
    if primary:
        s = df[primary].dropna()
        if len(s) > 10:
            z = (s - s.mean()) / (s.std() + 1e-9)
            n_anomalies = (z.abs() > 3).sum()
            if n_anomalies > 0:
                insights.append({
                    "icon": "⚠️",
                    "title": "Possible Anomaly",
                    "body": f"Found <b>{n_anomalies}</b> extreme value(s) in <b>{primary}</b> (z-score > 3). Verify these records.",
                    "highlight": None,
                })

    # 4. Missing values note
    miss_pct = df.isna().sum().sum() / (df.shape[0] * df.shape[1] + 1e-9) * 100
    if miss_pct > 5:
        insights.append({
            "icon": "❗",
            "title": "Data Quality Alert",
            "body": f"Dataset has <b>{miss_pct:.1f}%</b> missing values. Consider imputation before modeling.",
            "highlight": None,
        })

    # 5. Top performer (numeric max row)
    if primary and schema["categorical"]:
        cat_col = schema["categorical"][0]
        top_row = df.loc[df[primary].idxmax()] if primary in df.columns else None
        if top_row is not None:
            top_name = str(top_row[cat_col])[:40]
            insights.append({
                "icon": "⭐",
                "title": "Top Record",
                "body": f"Highest <b>{primary}</b> belongs to <b>{top_name}</b>.",
                "highlight": fmt_number(top_row[primary]),
            })

    # 6. Recommendation
    insights.append({
        "icon": "💡",
        "title": "Recommendation",
        "body": ("Focus on the top categories to maximize impact. Consider "
                 "investigating anomalies and missing-value patterns for data quality improvements."),
        "highlight": None,
    })

    return insights[:7]


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
RTL_CSS = """
<style>
html, body, .stApp, .stMarkdown, .stSidebar { direction: rtl; text-align: right; }
.kpi-grid, .insight-grid, .meta-row { direction: rtl; }
</style>
"""

def inject_theme():
    lang = st.session_state.get("lang", "en")
    if lang == "ar":
        st.markdown(RTL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ENHANCED GLASSMORPHISM CSS (appended)
# ─────────────────────────────────────────────
EXTRA_CSS = """
<style>
/* ── Display mode font scaling ── */
body.mode-compact * { font-size: calc(1em * 0.88) !important; }
body.mode-compact .kpi-value { font-size: 1.7rem !important; }
body.mode-compact .kpi-grid  { gap: 10px !important; }
body.mode-large   .kpi-value { font-size: 2.5rem !important; }
body.mode-large   .dash-title { font-size: 2.7rem !important; }

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
        "display_mode": "normal",
        "data_preview_page": 0,
        # SaaS persistence
        "dashboards": {},          # {dashboard_id: dashboard_meta_dict}
        "active_dashboard_id": None,
        "plan": "free",            # "free" or "pro"
        "session_id": None,
        "current_page": "dashboard",  # "dashboard" | "my_dashboards" | "history"
        "ai_chat_history": [],
        "ai_provider": "openai",
        "openai_api_key": "",
        "gemini_api_key": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state.session_id is None:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())[:8].upper()


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

        # Display mode
        display_mode = st.radio(
            "Display Mode",
            options=["compact", "normal", "large"],
            format_func=lambda x: {"compact": "⊟ Compact", "normal": "◻ Normal", "large": "⊞ Large Fonts"}[x],
            index=["compact", "normal", "large"].index(st.session_state.get("display_mode", "normal")),
            horizontal=True,
            key="display_mode_radio"
        )
        st.session_state.display_mode = display_mode
        # Inject display mode class
        if display_mode != "normal":
            st.markdown(f"""<script>document.body.classList.remove('mode-compact','mode-large');document.body.classList.add('mode-{display_mode}');</script>""", unsafe_allow_html=True)


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
# DOWNLOAD SECTION
# ─────────────────────────────────────────────
def render_download_section(df: pd.DataFrame, health: dict, file_label: str):
    section_header(t("download"), "Export")

    def to_csv_bytes(df):
        return df.to_csv(index=False).encode("utf-8-sig")

    def to_excel_bytes(df):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
            summary = pd.DataFrame({
                "Metric": ["Rows", "Columns", "Missing Cells", "Duplicate Rows", "Health Score"],
                "Value":  [len(df), len(df.columns), health["missing_cells"], health["dup_rows"], health["score"]]
            })
            summary.to_excel(writer, index=False, sheet_name="Summary")
        return buf.getvalue()

    def to_pdf_bytes(df, label):
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
    section_header(t("metadata"), "Info")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dash_id = "DB-" + hashlib.md5(file_label.encode()).hexdigest()[:8].upper()
    dataset_type = ("Time Series" if schema["date"] else
                    "Cross-sectional" if schema["categorical"] else "Numeric Only")

    items = [
        ("📁 File Name",        file_label),
        ("🆔 Dashboard ID",     dash_id),
        ("📅 Creation Date",    now),
        ("🔄 Last Update",      now),
        ("📊 Template",         template),
        ("🗂️ Dataset Type",     dataset_type),
        ("📦 Total Rows",       f"{len(df):,}"),
        ("⚙️ Columns",          str(len(df.columns))),
        ("🔢 Numeric Cols",     str(len(schema["numeric"]))),
        ("🏷️ Categorical Cols", str(len(schema["categorical"]))),
        ("📅 Date Cols",        str(len(schema["date"]))),
        ("🩺 Health Score",     f"{health['score']}/100 (Grade {health['grade']})"),
        ("❌ Missing Cells",    f"{health['missing_cells']:,} ({health['missing_pct']}%)"),
        ("🔁 Duplicate Rows",   f"{health['dup_rows']:,} ({health['dup_pct']}%)"),
        ("💾 Memory",           f"{df.memory_usage(deep=True).sum() // 1024:,} KB"),
    ]

    grid_html = "<div class='meta-info-grid'>" + "".join(
        f"<div class='meta-info-item'><div class='meta-info-label'>{label}</div><div class='meta-info-value'>{val}</div></div>"
        for label, val in items
    ) + "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ENHANCED SIDEBAR
# ─────────────────────────────────────────────
def render_enhanced_sidebar(df_raw, schema):
    """Render the settings panel + filters together, returning filtered df."""
    render_settings_panel()
    st.sidebar.markdown("<div class='sidebar-section'>Filters</div>", unsafe_allow_html=True)
    filtered = render_sidebar_filters(df_raw, schema)
    return filtered


# ─────────────────────────────────────────────
# AI ANALYST STYLES
# ─────────────────────────────────────────────
AI_ANALYST_CSS = """
<style>
/* ── AI Analyst tab ── */
.ai-chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 14px;
    max-height: 540px;
    overflow-y: auto;
    padding: 1.2rem 1rem;
    background: rgba(13,15,20,0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    scroll-behavior: smooth;
}
.chat-msg-user {
    align-self: flex-end;
    background: rgba(79,142,247,0.18);
    border: 1px solid rgba(79,142,247,0.3);
    border-radius: 14px 14px 4px 14px;
    padding: .75rem 1.1rem;
    max-width: 76%;
    font-size: .9rem;
    color: #e8edf5;
    line-height: 1.55;
}
.chat-msg-ai {
    align-self: flex-start;
    background: rgba(24,29,42,0.9);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 4px 14px 14px 14px;
    padding: .85rem 1.2rem;
    max-width: 88%;
    font-size: .9rem;
    color: #c4cdd8;
    line-height: 1.65;
    position: relative;
}
.chat-msg-ai::before {
    content: '◈';
    position: absolute;
    top: -10px; left: -4px;
    font-size: .8rem;
    color: #4f8ef7;
    background: #080a0f;
    padding: 0 4px;
    border-radius: 4px;
}
.chat-timestamp {
    font-size: .65rem;
    color: #556070;
    margin-top: 4px;
    text-align: right;
}
.suggested-btns {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: .75rem 0;
}
.suggested-btn {
    background: rgba(79,142,247,0.08);
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: 99px;
    padding: 6px 14px;
    font-size: .78rem;
    font-weight: 600;
    color: var(--accent1);
    cursor: pointer;
    transition: background .2s, border-color .2s;
    font-family: 'Inter', sans-serif;
}
.suggested-btn:hover {
    background: rgba(79,142,247,0.18);
    border-color: rgba(79,142,247,0.45);
}
/* API key input */
.api-config-box {
    background: rgba(19,22,31,0.85);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}

/* ── Executive Summary ── */
.exec-sum-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 14px;
    margin-top: .75rem;
}
.exec-sum-card {
    background: linear-gradient(135deg,rgba(24,29,42,0.95) 0%,rgba(19,22,31,0.95) 100%);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.exec-sum-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--ec, #4f8ef7), transparent);
    border-radius: 14px 14px 0 0;
}
.exec-sum-label {
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #556070;
    margin-bottom: .4rem;
}
.exec-sum-val {
    font-size: 1.05rem;
    font-weight: 700;
    color: #e8edf5;
    line-height: 1.4;
}
.exec-sum-sub {
    font-size: .75rem;
    color: #556070;
    margin-top: .3rem;
}

/* ── Smart insight cards (enhanced) ── */
.smart-ins-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 14px;
    margin-top: .5rem;
}
.smart-ins-card {
    background: var(--card2);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    display: flex;
    gap: 14px;
    align-items: flex-start;
    transition: transform .22s, border-color .22s, box-shadow .22s;
    position: relative;
    overflow: hidden;
}
.smart-ins-card:hover {
    transform: translateY(-2px);
    border-color: rgba(79,142,247,0.3);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}
.smart-ins-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--sc, #4f8ef7);
    opacity: 0.6;
}
.smart-ins-icon { font-size: 2rem; flex-shrink: 0; line-height: 1; margin-top: 2px; }
.smart-ins-title { font-size: .7rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; color: #556070; margin-bottom: .3rem; }
.smart-ins-body  { font-size: .88rem; color: #c4cdd8; line-height: 1.55; }
.smart-ins-val   { font-family: 'DM Mono',monospace; font-size: .95rem; font-weight: 700; color: var(--sc,#4f8ef7); display: block; margin-top: 5px; }

/* ── API toggle row ── */
.api-toggle-row {
    display: flex;
    gap: 10px;
    margin-bottom: .75rem;
}
.api-badge {
    padding: 5px 14px;
    border-radius: 99px;
    font-size: .75rem;
    font-weight: 700;
    cursor: pointer;
    transition: background .2s;
}
.api-badge-active {
    background: rgba(79,142,247,0.2);
    border: 1px solid rgba(79,142,247,0.5);
    color: #4f8ef7;
}
.api-badge-inactive {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    color: #556070;
}
</style>
"""

# ─────────────────────────────────────────────
# SMART INSIGHTS SECTION
# ─────────────────────────────────────────────
def render_smart_insights(df: pd.DataFrame, schema: dict, primary: str | None):
    """Render premium insight cards."""
    section_header("Smart Insights", "AI-powered")
    insights = generate_insights(df, schema, primary)

    COLORS = ["#4f8ef7", "#a78bfa", "#34d399", "#f59e0b", "#f87171", "#38bdf8", "#fb923c"]
    cards_html = '<div class="smart-ins-grid">'
    for i, ins in enumerate(insights):
        c = COLORS[i % len(COLORS)]
        highlight_html = f"<span class='smart-ins-val' style='color:{c}'>{ins['highlight']}</span>" if ins.get("highlight") else ""
        cards_html += f"""
        <div class='smart-ins-card' style='--sc:{c}'>
            <div class='smart-ins-icon'>{ins["icon"]}</div>
            <div style='flex:1;min-width:0'>
                <div class='smart-ins-title'>{ins["title"]}</div>
                <div class='smart-ins-body'>{ins["body"]}</div>
                {highlight_html}
            </div>
        </div>"""
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# EXECUTIVE SUMMARY
# ─────────────────────────────────────────────
def render_executive_summary(df: pd.DataFrame, schema: dict, primary: str | None, health: dict):
    """Render an AI Executive Summary card block near the top of the dashboard."""
    st.markdown(AI_ANALYST_CSS, unsafe_allow_html=True)
    section_header("Executive Summary", "Auto-generated")

    # Compute values
    best_cat_name = best_cat_val = worst_cat_name = worst_cat_val = "—"
    if primary and schema["categorical"]:
        cat_col = schema["categorical"][0]
        grp = df.groupby(cat_col, observed=True)[primary].sum()
        best_cat_name  = str(grp.idxmax())
        best_cat_val   = fmt_number(grp.max())
        worst_cat_name = str(grp.idxmin())
        worst_cat_val  = fmt_number(grp.min())

    highest_label = highest_val = "—"
    if primary:
        highest_val   = fmt_number(df[primary].max())
        highest_label = primary

    total_label = total_val = "—"
    if primary:
        total_val   = fmt_number(df[primary].sum())
        total_label = f"Total {primary}"

    date_range_str = "—"
    if schema["date"]:
        dcol = schema["date"][0]
        mn, mx = df[dcol].min(), df[dcol].max()
        if pd.notna(mn) and pd.notna(mx):
            date_range_str = f"{mn.strftime('%b %Y')} → {mx.strftime('%b %Y')}"

    cards = [
        ("#4f8ef7", "📁 Dataset Overview",   f"{len(df):,} rows × {len(df.columns)} cols",   f"Health {health['score']}/100 · Grade {health['grade']}"),
        ("#34d399", "🏆 Best Category",       best_cat_name,                                    f"{schema['categorical'][0] if schema['categorical'] else ''} · {best_cat_val}"),
        ("#f87171", "📉 Worst Category",      worst_cat_name,                                   f"{schema['categorical'][0] if schema['categorical'] else ''} · {worst_cat_val}"),
        ("#f59e0b", "⚡ Highest Value",        highest_val,                                      f"Max {highest_label}"),
        ("#a78bfa", "📅 Date Coverage",       date_range_str,                                   f"{len(schema['date'])} date column(s)"),
        ("#38bdf8", "📊 Key Observation",     f"{len(schema['numeric'])} numeric / {len(schema['categorical'])} categorical cols",
                                               f"Missing: {health['missing_pct']}% · Dupes: {health['dup_pct']}%"),
    ]

    grid_html = '<div class="exec-sum-grid">'
    for color, label, val, sub in cards:
        grid_html += f"""
        <div class='exec-sum-card' style='--ec:{color}'>
            <div class='exec-sum-label'>{label}</div>
            <div class='exec-sum-val'>{val}</div>
            <div class='exec-sum-sub'>{sub}</div>
        </div>"""
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BUILD DATASET CONTEXT (for AI prompt)
# ─────────────────────────────────────────────
def build_dataset_context(df: pd.DataFrame, schema: dict, primary: str | None, health: dict) -> str:
    """Build a compact textual summary of the dataset to inject into AI prompts."""
    lines = [
        f"Dataset: {len(df):,} rows × {len(df.columns)} columns.",
        f"Numeric columns: {', '.join(schema['numeric'][:10]) or 'none'}.",
        f"Categorical columns: {', '.join(schema['categorical'][:10]) or 'none'}.",
        f"Date columns: {', '.join(schema['date'][:5]) or 'none'}.",
        f"Primary measure: {primary or 'none'}.",
        f"Health score: {health['score']}/100 (Grade {health['grade']}).",
        f"Missing values: {health['missing_pct']}%.",
        f"Duplicate rows: {health['dup_rows']} ({health['dup_pct']}%).",
    ]
    if primary and schema["categorical"]:
        cat_col = schema["categorical"][0]
        grp = df.groupby(cat_col, observed=True)[primary].sum().nlargest(5)
        top5 = ", ".join([f"{k}: {fmt_number(v)}" for k, v in grp.items()])
        lines.append(f"Top 5 {cat_col} by {primary}: {top5}.")
    if primary:
        s = df[primary].dropna()
        lines.append(f"{primary} stats: min={fmt_number(s.min())}, max={fmt_number(s.max())}, mean={fmt_number(s.mean())}, sum={fmt_number(s.sum())}.")
    if primary and schema["date"]:
        dcol = schema["date"][0]
        try:
            tmp = df[[dcol, primary]].dropna().copy()
            tmp[dcol] = pd.to_datetime(tmp[dcol])
            monthly = tmp.set_index(dcol).resample("ME")[primary].sum()
            if len(monthly) >= 2:
                prev, curr = monthly.iloc[-2], monthly.iloc[-1]
                pct = (curr - prev) / (abs(prev) + 1e-9) * 100
                lines.append(f"Last-month {primary} change: {pct:+.1f}%.")
        except Exception:
            pass
    return " ".join(lines)


# ─────────────────────────────────────────────
# AI ANALYST TAB
# ─────────────────────────────────────────────
SUGGESTED_QUESTIONS = [
    "Explain this dashboard",
    "Which category performs best?",
    "Which region performs worst?",
    "Show anomalies",
    "Show trends",
    "Give recommendations",
    "Summarize the dataset",
    "Top products",
    "Top customers",
]

def call_openai(messages: list[dict], api_key: str) -> str:
    """Call OpenAI chat completions API."""
    import urllib.request, json
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def call_gemini(messages: list[dict], api_key: str) -> str:
    """Call Gemini generateContent API."""
    import urllib.request, json
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    contents_clean = [c for c in contents if c["role"] in ("user", "model")]
    if not contents_clean:
        contents_clean = [{"role": "user", "parts": [{"text": "Hello"}]}]

    payload = json.dumps({"contents": contents_clean, "generationConfig": {"maxOutputTokens": 800, "temperature": 0.7}}).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"]


def render_ai_analyst_tab(df: pd.DataFrame, schema: dict, primary: str | None, health: dict):
    """Render the 🤖 AI Analyst tab content."""
    st.markdown(AI_ANALYST_CSS, unsafe_allow_html=True)

    # ── API Provider Config ──
    with st.expander("⚙️ AI Provider Configuration", expanded=False):
        ai_provider = st.radio(
            "Select AI Provider",
            options=["OpenAI (GPT-4o mini)", "Google Gemini"],
            horizontal=True,
            key="ai_provider_radio",
        )
        if "OpenAI" in ai_provider:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                key="openai_api_key",
            )
            st.session_state.ai_provider = "openai"
        else:
            api_key = st.text_input(
                "Google Gemini API Key",
                type="password",
                placeholder="AIza...",
                key="gemini_api_key",
            )
            st.session_state.ai_provider = "gemini"
        st.caption("Keys are stored only in this session and never sent anywhere except the AI provider's API.")

    provider_short = st.session_state.get("ai_provider", "openai")

    # ── Session state for chat ──
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # Dataset context (cached per file)
    ctx = build_dataset_context(df, schema, primary, health)
    system_prompt = (
        "You are an expert data analyst assistant embedded in a dynamic dashboard. "
        "Answer questions concisely and insightfully about the user's dataset. "
        "Use bullet points and bold text for key numbers. Be professional but friendly. "
        f"Here is the dataset context:\n{ctx}"
    )

    # ── Suggested questions ──
    st.markdown("<div style='font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#556070;margin-bottom:.5rem'>Suggested questions</div>", unsafe_allow_html=True)
    sq_cols = st.columns(3)
    for idx, q in enumerate(SUGGESTED_QUESTIONS):
        with sq_cols[idx % 3]:
            if st.button(q, key=f"sq_{idx}", use_container_width=True):
                st.session_state.ai_pending_question = q

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Chat history display ──
    chat_html = '<div class="ai-chat-wrap" id="ai-chat-box">'
    if not st.session_state.ai_chat_history:
        chat_html += """
        <div style='text-align:center;padding:2rem 0;color:#556070;font-size:.88rem'>
            <div style='font-size:2rem;margin-bottom:.5rem'>◈</div>
            Ask me anything about your dataset — or pick a suggested question above.
        </div>"""
    else:
        for msg in st.session_state.ai_chat_history:
            ts = msg.get("ts", "")
            if msg["role"] == "user":
                chat_html += f"<div class='chat-msg-user'>{msg['content']}<div class='chat-timestamp'>{ts}</div></div>"
            else:
                content = _re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", msg["content"].replace("\n", "<br>"))
                chat_html += f"<div class='chat-msg-ai'>{content}<div class='chat-timestamp'>{ts}</div></div>"
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # Auto-scroll JS
    st.markdown("""
    <script>
    var chatBox = document.getElementById('ai-chat-box');
    if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
    </script>
    """, unsafe_allow_html=True)

    # ── Input row ──
    input_col, btn_col, clr_col = st.columns([7, 1, 1])
    with input_col:
        pending = st.session_state.pop("ai_pending_question", None)
        user_input = st.text_input(
            "Ask the AI analyst…",
            value=pending or "",
            placeholder="e.g. Which category has the highest growth?",
            label_visibility="collapsed",
            key="ai_user_input",
        )
    with btn_col:
        send_clicked = st.button("Send ➤", use_container_width=True, key="ai_send_btn")
    with clr_col:
        if st.button("🗑 Clear", use_container_width=True, key="ai_clear_btn"):
            st.session_state.ai_chat_history = []
            st.rerun()

    # ── Process message ──
    if (send_clicked or pending) and (user_input or pending):
        question = (user_input or pending).strip()
        if not question:
            st.warning("Please enter a question.")
            return

        resolved_key = api_key or st.session_state.get("openai_api_key", "") or st.session_state.get("gemini_api_key", "")

        if not resolved_key:
            st.warning("⚠️ Please enter your API key in the configuration panel above.")
            return

        ts = datetime.datetime.now().strftime("%H:%M")
        st.session_state.ai_chat_history.append({"role": "user", "content": question, "ts": ts})

        # Build message list for API
        messages_api = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.ai_chat_history[:-1]:
            if m["role"] in ("user", "assistant"):
                messages_api.append({"role": m["role"], "content": m["content"]})
        messages_api.append({"role": "user", "content": question})

        with st.spinner("◈ Thinking…"):
            try:
                if provider_short == "openai":
                    answer = call_openai(messages_api, resolved_key)
                else:
                    answer = call_gemini(messages_api, resolved_key)
            except Exception as e:
                answer = f"⚠️ API error: {str(e)[:200]}\n\nPlease verify your API key and try again."

        ai_ts = datetime.datetime.now().strftime("%H:%M")
        st.session_state.ai_chat_history.append({"role": "assistant", "content": answer, "ts": ai_ts})
        st.rerun()


# ─────────────────────────────────────────────
# SAAS FEATURES — DASHBOARD PERSISTENCE, HISTORY, PUBLIC LINKS, PLANS
# ─────────────────────────────────────────────
SAAS_CSS = """
<style>
/* ── Plan badge ── */
.plan-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 12px;
    border-radius: 99px;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.plan-free { background: rgba(100,116,139,0.15); border: 1px solid rgba(100,116,139,0.3); color: #94a3b8; }
.plan-pro  { background: rgba(167,139,250,0.15); border: 1px solid rgba(167,139,250,0.4); color: #a78bfa; }

/* ── Dashboard card (My Dashboards page) ── */
.db-card {
    background: linear-gradient(135deg, rgba(24,29,42,0.95) 0%, rgba(19,22,31,0.95) 100%);
    border: 1px solid rgba(255,255,255,0.085);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    transition: border-color .25s, transform .25s, box-shadow .25s;
    margin-bottom: 14px;
}
.db-card:hover {
    border-color: rgba(79,142,247,0.35);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 30px rgba(79,142,247,0.1);
}
.db-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4f8ef7, #a78bfa, transparent);
}
.db-card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #e8edf5;
    margin-bottom: .3rem;
    letter-spacing: -.01em;
}
.db-card-sub {
    font-size: .8rem;
    color: #556070;
    margin-bottom: .85rem;
}
.db-card-meta {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: .85rem;
}
.db-meta-chip {
    font-size: .68rem;
    font-weight: 600;
    padding: 2px 9px;
    border-radius: 99px;
    background: rgba(79,142,247,0.08);
    border: 1px solid rgba(79,142,247,0.15);
    color: #7fb3f7;
    letter-spacing: .02em;
}
.db-card-actions {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    margin-top: .5rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: .75rem;
}
.db-action-btn {
    font-size: .73rem;
    font-weight: 600;
    padding: 4px 13px;
    border-radius: 8px;
    cursor: pointer;
    border: 1px solid rgba(79,142,247,0.25);
    background: rgba(79,142,247,0.08);
    color: #4f8ef7;
    transition: background .18s, border-color .18s;
    white-space: nowrap;
}
.db-action-btn:hover { background: rgba(79,142,247,0.18); border-color: rgba(79,142,247,0.5); }
.db-action-danger { border-color: rgba(248,113,113,0.25); background: rgba(248,113,113,0.06); color: #f87171; }
.db-action-danger:hover { background: rgba(248,113,113,0.15); border-color: rgba(248,113,113,0.5); }
.db-action-green { border-color: rgba(52,211,153,0.25); background: rgba(52,211,153,0.06); color: #34d399; }
.db-action-green:hover { background: rgba(52,211,153,0.15); }

/* ── Status badges ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: .68rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 99px;
    letter-spacing: .04em;
}
.status-active { background: rgba(52,211,153,0.12); border: 1px solid rgba(52,211,153,0.3); color: #34d399; }
.status-soon   { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.3); color: #f59e0b; }
.status-expired{ background: rgba(248,113,113,0.12); border: 1px solid rgba(248,113,113,0.3); color: #f87171; }

/* ── Share panel ── */
.share-panel {
    background: rgba(13,15,20,0.7);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-top: .75rem;
}
.share-id-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: .55rem 1rem;
    font-family: 'DM Mono', monospace;
    font-size: .82rem;
    color: #7fb3f7;
    margin-bottom: .75rem;
}
.share-meta-row {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    font-size: .78rem;
    color: #556070;
    margin-top: .5rem;
}
.share-meta-row span { color: #c4cdd8; font-weight: 600; }

/* ── Page nav pills ── */
.page-nav {
    display: flex;
    gap: 6px;
    margin-bottom: 1.5rem;
}
.page-nav-pill {
    padding: 6px 16px;
    border-radius: 10px;
    font-size: .8rem;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.03);
    color: #556070;
    cursor: pointer;
    transition: background .18s, color .18s, border-color .18s;
}
.page-nav-pill.active {
    background: rgba(79,142,247,0.15);
    border-color: rgba(79,142,247,0.35);
    color: #4f8ef7;
}

/* ── Plan upgrade banner ── */
.upgrade-banner {
    background: linear-gradient(135deg, rgba(167,139,250,0.12) 0%, rgba(79,142,247,0.08) 100%);
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 1.5rem;
}
.upgrade-banner-text { font-size: .88rem; color: #c4cdd8; }
.upgrade-banner-text b { color: #a78bfa; }

/* ── History page ── */
.hist-card {
    background: rgba(19,22,31,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 10px;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr auto;
    align-items: center;
    gap: 12px;
    transition: border-color .2s, box-shadow .2s;
}
.hist-card:hover {
    border-color: rgba(79,142,247,0.25);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.hist-card-name { font-size: .9rem; font-weight: 700; color: #e8edf5; }
.hist-card-sub  { font-size: .72rem; color: #556070; margin-top: 2px; }
.hist-col-label { font-size: .65rem; font-weight: 700; text-transform: uppercase; letter-spacing: .09em; color: #556070; }
.hist-col-val   { font-size: .85rem; font-weight: 600; color: #c4cdd8; font-family: 'DM Mono', monospace; }

/* ── Countdown card ── */
.countdown-card {
    background: linear-gradient(135deg, rgba(24,29,42,0.95) 0%, rgba(19,22,31,0.95) 100%);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 12px;
    padding: .9rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.countdown-days {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'DM Mono', monospace;
    color: #f59e0b;
    line-height: 1;
}
</style>
"""

# ─────────────────────────────────────────────
# SAAS HELPERS
# ─────────────────────────────────────────────
import uuid as _uuid
import datetime as _dt
import json as _json
import hashlib as _hashlib
import base64 as _b64


def _new_dashboard_id() -> str:
    return "DB-" + str(_uuid.uuid4())[:8].upper()


def _now_iso() -> str:
    return _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")


def _expiry_date(plan: str) -> str:
    days = 30 if plan == "free" else 36500  # ~100 years for pro
    exp = _dt.datetime.utcnow() + _dt.timedelta(days=days)
    return exp.strftime("%Y-%m-%d")


def _days_remaining(expiry_str: str) -> int:
    try:
        exp = _dt.datetime.strptime(expiry_str, "%Y-%m-%d")
        return max(0, (exp - _dt.datetime.utcnow()).days)
    except Exception:
        return 0


def _status_badge(days: int) -> str:
    if days > 7:
        return "<span class='status-badge status-active'>🟢 Active</span>"
    elif days > 0:
        return "<span class='status-badge status-soon'>🟡 Expires Soon</span>"
    else:
        return "<span class='status-badge status-expired'>🔴 Expired</span>"


def _dashboard_url(dash_id: str) -> str:
    # Use local query param approach
    return f"?dashboard={dash_id}"


def save_dashboard(file_name: str, rows: int, cols: int, template: str) -> dict:
    """Create and persist a new dashboard record."""
    plan = st.session_state.get("plan", "free")
    dashboards = st.session_state.get("dashboards", {})

    # Free plan: max 1 dashboard, prompt before overwrite
    if plan == "free" and len(dashboards) >= 1:
        # Show warning and ask user to confirm overwrite
        if not st.sidebar.button("⚠️ Overwrite existing dashboard", key="overwrite_warning"):
            st.sidebar.warning("Free plan allows only 1 dashboard. Click 'Overwrite existing dashboard' to replace it.")
            return None
        existing_id = list(dashboards.keys())[0]
        dash_id = existing_id
    else:
        dash_id = _new_dashboard_id()

    now = _now_iso()
    record = {
        "id":           dash_id,
        "name":         file_name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title(),
        "dataset":      file_name,
        "created":      dashboards.get(dash_id, {}).get("created", now),
        "last_updated": now,
        "expiry":       _expiry_date(plan),
        "url":          _dashboard_url(dash_id),
        "plan":         plan,
        "session_id":   st.session_state.get("session_id", "—"),
        "rows":         rows,
        "cols":         cols,
        "template":     template,
        "last_opened":  now,
    }
    dashboards[dash_id] = record
    st.session_state.dashboards = dashboards
    st.session_state.active_dashboard_id = dash_id
    return record


def get_active_dashboard() -> dict | None:
    aid = st.session_state.get("active_dashboard_id")
    return st.session_state.get("dashboards", {}).get(aid)


def delete_dashboard(dash_id: str):
    dashboards = st.session_state.get("dashboards", {})
    dashboards.pop(dash_id, None)
    st.session_state.dashboards = dashboards
    if st.session_state.get("active_dashboard_id") == dash_id:
        st.session_state.active_dashboard_id = None


def duplicate_dashboard(dash_id: str):
    dashboards = st.session_state.get("dashboards", {})
    if dash_id not in dashboards:
        return
    plan = st.session_state.get("plan", "free")
    if plan == "free":
        st.warning("⚠️ Upgrade to Pro to duplicate dashboards.")
        return
    orig = dashboards[dash_id].copy()
    new_id = _new_dashboard_id()
    orig["id"] = new_id
    orig["name"] = orig["name"] + " (Copy)"
    orig["created"] = _now_iso()
    orig["last_updated"] = _now_iso()
    dashboards[new_id] = orig
    st.session_state.dashboards = dashboards


# ─────────────────────────────────────────────
# PLAN TOGGLE (sidebar)
# ─────────────────────────────────────────────
def render_plan_toggle():
    plan = st.session_state.get("plan", "free")
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div class='sidebar-section'>Plan</div>", unsafe_allow_html=True)
    if plan == "free":
        badge_html = "<span class='plan-badge plan-free' style='font-size:.7rem'>⚡ Free</span>"
    else:
        badge_html = "<span class='plan-badge plan-pro' style='font-size:.7rem'>✦ Pro</span>"
    st.sidebar.markdown(badge_html, unsafe_allow_html=True)
    if st.sidebar.button("🔄 Toggle Plan (Demo)", key="toggle_plan_btn", use_container_width=True):
        st.session_state.plan = "pro" if plan == "free" else "free"
        st.rerun()
    plan_label = "Pro" if plan == "pro" else "Free"
    st.sidebar.caption(f"Current: **{plan_label}** · Session `{st.session_state.get('session_id', '—')}`")


# ─────────────────────────────────────────────
# PAGE NAV (sidebar)
# ─────────────────────────────────────────────
def render_page_nav():
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div class='sidebar-section'>Navigation</div>", unsafe_allow_html=True)
    pages = [
        ("dashboard",     "📊 Dashboard"),
        ("my_dashboards", "📂 My Dashboards"),
        ("history",       "🕑 History"),
    ]
    current = st.session_state.get("current_page", "dashboard")
    for page_id, label in pages:
        active = "✓ " if current == page_id else ""
        if st.sidebar.button(f"{active}{label}", key=f"nav_{page_id}", use_container_width=True):
            st.session_state.current_page = page_id
            st.rerun()


# ─────────────────────────────────────────────
# SHARE PANEL (rendered inline)
# ─────────────────────────────────────────────
def render_share_panel(record: dict):
    days = _days_remaining(record.get("expiry", "2099-01-01"))
    status_html = _status_badge(days)
    url = record.get("url", "—")
    st.markdown(f"""
    <div class='share-panel'>
        <div style='font-size:.8rem;font-weight:700;color:#556070;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.75rem'>
            🔗 Public Link & Dashboard ID
        </div>
        <div class='share-id-row'>
            <span>🆔 {record["id"]}</span>
            {status_html}
        </div>
        <div class='share-id-row'>
            <span style='font-size:.75rem;word-break:break-all'>{url}</span>
        </div>
        <div class='share-meta-row'>
            <div>Created: <span>{record.get("created","—")}</span></div>
            <div>Expires: <span>{record.get("expiry","—")}</span></div>
            <div>Remaining: <span>{days} days</span></div>
            <div>Plan: <span>{record.get("plan","free").upper()}</span></div>
            <div>Session: <span>{record.get("session_id","—")}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.text_input("📋 Copy Dashboard URL", value=url, key="share_url_input", label_visibility="collapsed")
    st.caption("↑ Click the field above and press Ctrl+A, Ctrl+C to copy the dashboard link.")


# ─────────────────────────────────────────────
# MY DASHBOARDS PAGE
# ─────────────────────────────────────────────
def render_my_dashboards_page():
    st.markdown(SAAS_CSS, unsafe_allow_html=True)
    plan = st.session_state.get("plan", "free")
    dashboards = st.session_state.get("dashboards", {})

    st.markdown(f"""
    <div style='padding:1.5rem 0 .5rem'>
        <div class='dash-title'>📂 My Dashboards</div>
        <div class='dash-sub'>Manage, share, and revisit your saved dashboards</div>
        <div style='margin-top:.6rem'>
            <span class='plan-badge {"plan-pro" if plan=="pro" else "plan-free"}'>
                {"✦ Pro Plan" if plan=="pro" else "⚡ Free Plan"}
            </span>
            &nbsp;
            <span class='hbadge'>{len(dashboards)} / {"∞" if plan=="pro" else "1"} dashboards</span>
            &nbsp;
            <span class='hbadge-green'>Session {st.session_state.get("session_id","—")}</span>
        </div>
    </div>
    <hr class='divider'>
    """, unsafe_allow_html=True)

    if not dashboards:
        st.markdown
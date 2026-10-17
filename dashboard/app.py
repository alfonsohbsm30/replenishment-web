"""
app.py  ·  Smart Inventory Replenishment Dashboard
===================================================
Portfolio project — AI-assisted demand forecasting and inventory risk analysis.

Run from the project root:
    streamlit run dashboard/app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Inventory Intelligence · Smart Replenishment",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# Theme: "Analytical Luxury" — deep navy base, electric cyan accent,
#        Geist Mono for data, Outfit for UI copy.
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Geist+Mono:wght@300;400;500;600&display=swap');

/* ─── Design tokens ───────────────────────────────────────── */
:root {
  --navy-950:    #030712;
  --navy-900:    #060B18;
  --navy-800:    #0C1428;
  --navy-700:    #111D38;
  --navy-600:    #162447;
  --border-dim:  rgba(255,255,255,0.06);
  --border-mid:  rgba(255,255,255,0.10);
  --border-hi:   rgba(255,255,255,0.18);
  --cyan:        #00D4FF;
  --cyan-dim:    rgba(0,212,255,0.10);
  --cyan-glow:   rgba(0,212,255,0.20);
  --emerald:     #00E5A0;
  --emerald-dim: rgba(0,229,160,0.10);
  --rose:        #FF4D6D;
  --rose-dim:    rgba(255,77,109,0.10);
  --amber:       #FFB547;
  --amber-dim:   rgba(255,181,71,0.10);
  --violet:      #A78BFA;
  --violet-dim:  rgba(167,139,250,0.10);
  --sky:         #38BDF8;
  --txt-primary:   #F0F6FF;
  --txt-secondary: #8BA3C7;
  --txt-muted:     #4A6080;
  --txt-dim:       #2D4060;
  --font-ui:   'Outfit', sans-serif;
  --font-data: 'Geist Mono', monospace;
}

/* ─── Global ──────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
  font-family: var(--font-ui) !important;
  background-color: var(--navy-900) !important;
  color: var(--txt-primary) !important;
}
.stApp {
  background-image:
    radial-gradient(circle at 20% 10%, rgba(0,212,255,0.04) 0%, transparent 50%),
    radial-gradient(circle at 80% 90%, rgba(0,229,160,0.03) 0%, transparent 50%),
    radial-gradient(rgba(255,255,255,0.018) 1px, transparent 1px) !important;
  background-size: 100% 100%, 100% 100%, 28px 28px !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 0 2.5rem 4rem !important; max-width: 1440px !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--navy-900); }
::-webkit-scrollbar-thumb { background: var(--navy-600); border-radius: 4px; }

/* ─── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--navy-950) !important;
  border-right: 1px solid var(--border-dim) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
.sidebar-logo {
  padding: 1.75rem 1.5rem 1.25rem;
  border-bottom: 1px solid var(--border-dim);
  margin-bottom: 1.5rem;
}
.sidebar-logo .logo-mark {
  font-size: 1.4rem; font-weight: 800; color: var(--cyan);
  letter-spacing: -.03em; font-family: var(--font-data); line-height: 1;
}
.sidebar-logo .logo-sub {
  font-size: .68rem; font-weight: 500; color: var(--txt-muted);
  letter-spacing: .12em; text-transform: uppercase; margin-top: .4rem;
}
.sidebar-section-label {
  font-size: .62rem; font-weight: 700; letter-spacing: .15em;
  text-transform: uppercase; color: var(--txt-dim); padding: 0 1rem .5rem;
  margin-bottom: .25rem;
}
[data-testid="stSidebar"] label {
  font-size: .72rem !important; font-weight: 600 !important;
  letter-spacing: .08em !important; text-transform: uppercase !important;
  color: var(--txt-secondary) !important; margin-bottom: .25rem !important;
}
[data-baseweb="select"] > div {
  background: var(--navy-800) !important; border-color: var(--border-mid) !important;
}
.sidebar-stats {
  margin: 1.5rem 1rem .5rem; padding: 1rem;
  background: var(--navy-800); border: 1px solid var(--border-dim); border-radius: 8px;
}
.stat-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: .3rem 0; border-bottom: 1px solid var(--border-dim);
}
.stat-row:last-child { border-bottom: none; }
.stat-key { font-size: .68rem; color: var(--txt-muted); font-weight: 500; }
.stat-val { font-size: .72rem; color: var(--txt-secondary); font-family: var(--font-data); }

/* ─── Page hero ───────────────────────────────────────────── */
.page-hero {
  padding: 3rem 0 2.5rem; position: relative;
}
.page-hero::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--border-mid) 20%,
    var(--border-hi) 50%, var(--border-mid) 80%, transparent 100%);
}
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: .5rem;
  font-size: .65rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase;
  color: var(--cyan); background: var(--cyan-dim); border: 1px solid var(--cyan-glow);
  border-radius: 99px; padding: .3rem .85rem; margin-bottom: 1.1rem;
  font-family: var(--font-data);
}
.hero-eyebrow::before {
  content: ''; width: 6px; height: 6px; border-radius: 50%;
  background: var(--cyan); box-shadow: 0 0 8px var(--cyan);
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:.4; transform:scale(.7); }
}
.hero-title {
  font-size: clamp(1.8rem, 3vw, 2.6rem); font-weight: 800; color: var(--txt-primary);
  letter-spacing: -.04em; line-height: 1.1; margin-bottom: .6rem;
}
.hero-title span { color: var(--cyan); }
.hero-subtitle {
  font-size: .95rem; color: var(--txt-secondary); font-weight: 400;
  max-width: 560px; line-height: 1.6;
}
.hero-meta { display: flex; gap: 1.5rem; margin-top: 1.4rem; flex-wrap: wrap; }
.hero-meta-item {
  display: flex; align-items: center; gap: .4rem;
  font-size: .72rem; color: var(--txt-muted); font-family: var(--font-data);
}
.hero-meta-item .dot {
  width: 5px; height: 5px; border-radius: 50%; background: var(--emerald);
}

/* ─── Section headers ─────────────────────────────────────── */
.section-wrap { margin: 3.5rem 0 1.75rem; }
.section-rule { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem; }
.section-num {
  font-family: var(--font-data); font-size: .65rem; font-weight: 600; color: var(--cyan);
  background: var(--cyan-dim); border: 1px solid var(--cyan-glow); border-radius: 4px;
  padding: .2rem .5rem; letter-spacing: .1em; flex-shrink: 0;
}
.section-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--border-mid) 0%, transparent 100%);
}
.section-heading {
  font-size: 1.3rem; font-weight: 700; color: var(--txt-primary);
  letter-spacing: -.02em; margin-bottom: .3rem;
}
.section-desc { font-size: .8rem; color: var(--txt-muted); font-weight: 400; }

/* ─── KPI grid ────────────────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: .85rem; margin-bottom: 2.5rem;
}
.kpi-card {
  background: var(--navy-800); border: 1px solid var(--border-dim);
  border-radius: 10px; padding: 1.25rem 1.3rem 1.1rem; position: relative;
  overflow: hidden; transition: border-color .25s, transform .25s, box-shadow .25s;
}
.kpi-card:hover {
  border-color: var(--border-hi); transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(0,0,0,.4);
}
.kpi-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--kpi-color, var(--cyan)); opacity: .85;
}
.kpi-card::after {
  content: ''; position: absolute; top: -30px; right: -30px;
  width: 80px; height: 80px; border-radius: 50%;
  background: var(--kpi-color, var(--cyan)); opacity: .04;
  transition: opacity .25s;
}
.kpi-card:hover::after { opacity: .09; }
.kpi-label {
  font-size: .6rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
  color: var(--txt-muted); margin-bottom: .65rem;
}
.kpi-value {
  font-family: var(--font-data); font-size: 1.55rem; font-weight: 600;
  color: var(--txt-primary); line-height: 1; letter-spacing: -.02em;
}
.kpi-sub { font-size: .65rem; color: var(--txt-muted); margin-top: .5rem; }
.kpi-alert { color: var(--rose) !important; }
.kpi-warn  { color: var(--amber) !important; }
.kpi-ok    { color: var(--emerald) !important; }

/* ─── Chart label ─────────────────────────────────────────── */
.chart-label {
  font-size: .62rem; font-weight: 700; letter-spacing: .15em; text-transform: uppercase;
  color: var(--txt-muted); margin-bottom: 1rem; display: flex; align-items: center; gap: .5rem;
}
.chart-label::before {
  content: ''; width: 3px; height: 12px; background: var(--cyan);
  border-radius: 2px; flex-shrink: 0;
}

/* ─── Insight cards ───────────────────────────────────────── */
.insights-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: .5rem;
}
.insight-card {
  background: var(--navy-800); border: 1px solid var(--border-dim);
  border-radius: 10px; padding: 1.3rem 1.4rem; position: relative;
  overflow: hidden; transition: border-color .2s, transform .2s;
}
.insight-card:hover { border-color: var(--border-mid); transform: translateY(-2px); }
.insight-card::before {
  content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%;
  background: var(--ic-color, var(--cyan)); border-radius: 3px 0 0 3px;
}
.insight-tag {
  display: inline-flex; align-items: center; gap: .35rem;
  font-size: .6rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
  color: var(--ic-color, var(--cyan)); margin-bottom: .65rem; font-family: var(--font-data);
}
.insight-tag .ic-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--ic-color, var(--cyan)); flex-shrink: 0;
}
.insight-body {
  font-size: .84rem; line-height: 1.7; color: var(--txt-secondary); font-weight: 400;
}
.insight-body b, .insight-body strong { color: var(--txt-primary); font-weight: 600; }

/* ─── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important; border-bottom: 1px solid var(--border-dim) !important;
  gap: .25rem !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: var(--txt-muted) !important;
  font-size: .75rem !important; font-weight: 600 !important; letter-spacing: .04em !important;
  padding: .55rem 1.1rem !important; border-radius: 6px 6px 0 0 !important;
  border: 1px solid transparent !important; border-bottom: none !important;
}
.stTabs [aria-selected="true"] {
  background: var(--cyan-dim) !important; color: var(--cyan) !important;
  border-color: var(--border-mid) !important;
}

/* ─── Dataframe ───────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border-radius: 8px !important; overflow: hidden !important;
  border: 1px solid var(--border-dim) !important;
}

/* ─── Metric widget ───────────────────────────────────────── */
[data-testid="stMetricValue"] {
  font-family: var(--font-data) !important; font-size: 1.5rem !important;
}
[data-testid="stMetricLabel"] {
  font-size: .68rem !important; text-transform: uppercase !important;
  letter-spacing: .1em !important; color: var(--txt-muted) !important;
}
.stSelectbox label {
  font-size: .72rem !important; font-weight: 600 !important;
  letter-spacing: .08em !important; text-transform: uppercase !important;
  color: var(--txt-secondary) !important;
}

/* ─── Footer ──────────────────────────────────────────────── */
.dash-footer {
  margin-top: 4rem; padding: 1.5rem 0; border-top: 1px solid var(--border-dim);
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: .75rem;
}
.footer-left { display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }
.footer-pill {
  display: inline-flex; align-items: center; gap: .4rem; font-size: .65rem;
  font-weight: 600; letter-spacing: .08em; color: var(--txt-dim); font-family: var(--font-data);
}
.footer-pill .fp-dot { width: 4px; height: 4px; border-radius: 50%; background: var(--txt-dim); }
.footer-right { font-size: .65rem; color: var(--txt-dim); font-family: var(--font-data); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FILE PATHS  — robust, works from any cwd
# ─────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / "data" / "processed"
CLEANED_PATH  = DATA_DIR / "cleaned_inventory_sales.csv"
FORECAST_PATH = DATA_DIR / "product_demand_forecast.csv"
RECOM_PATH    = DATA_DIR / "inventory_recommendations.csv"


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    missing = [p for p in [CLEANED_PATH, FORECAST_PATH, RECOM_PATH] if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required data files:\n" +
            "\n".join(f"  ✗  {p}" for p in missing) +
            "\n\nRun the pipeline scripts in order:\n"
            "  python data_generator.py\n  python data_cleaning.py\n"
            "  python forecasting.py\n  python inventory_logic.py"
        )
    return (
        pd.read_csv(CLEANED_PATH,  parse_dates=["date"]),
        pd.read_csv(FORECAST_PATH),
        pd.read_csv(RECOM_PATH),
    )

try:
    cleaned_df, forecast_df, recom_df = load_data()
except FileNotFoundError as err:
    st.error("### ⚠  Data Pipeline Incomplete")
    st.code(str(err), language="text")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────────────────────────────────────
_FONT   = "Geist Mono, monospace"
_BG     = "rgba(0,0,0,0)"
_GRID   = "rgba(255,255,255,0.05)"
_TICK   = "#4A6080"
_TEXT   = "#8BA3C7"
_COLORS = ["#00D4FF","#00E5A0","#FFB547","#FF4D6D",
           "#A78BFA","#38BDF8","#FB923C","#34D399"]

THEME = dict(
    paper_bgcolor=_BG, plot_bgcolor=_BG,
    font=dict(family=_FONT, color=_TEXT, size=11),
    xaxis=dict(gridcolor=_GRID, linecolor=_GRID, zeroline=False,
               tickfont=dict(color=_TICK, size=10)),
    yaxis=dict(gridcolor=_GRID, linecolor=_GRID, zeroline=False,
               tickfont=dict(color=_TICK, size=10)),
    legend=dict(bgcolor=_BG, font=dict(color=_TEXT, size=10),
                bordercolor="rgba(0,0,0,0)"),
    margin=dict(l=4, r=4, t=36, b=4),
    colorway=_COLORS,
    hoverlabel=dict(bgcolor="#0C1428", font_size=12,
                    font_family=_FONT, bordercolor="rgba(255,255,255,0.15)"),
)

def themed(fig, title=""):
    if title:
        fig.update_layout(title=dict(
            text=title, font=dict(color="#C8D8F0", size=13, family=_FONT),
            x=0, pad=dict(l=2)))
    fig.update_layout(**THEME)
    return fig

def chart_label(text: str):
    st.markdown(f"<div class='chart-label'>{text}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <div class="logo-mark">◈ INVIQ</div>
      <div class="logo-sub">Smart Replenishment System</div>
    </div>
    <div class="sidebar-section-label">Filters</div>
    """, unsafe_allow_html=True)

    min_d = cleaned_df["date"].min().date()
    max_d = cleaned_df["date"].max().date()
    date_range = st.date_input("Date Range", value=(min_d, max_d),
                                min_value=min_d, max_value=max_d)
    start_d, end_d = (date_range if isinstance(date_range, (list, tuple))
                      and len(date_range) == 2 else (min_d, max_d))

    all_cats    = sorted(cleaned_df["category"].unique())
    all_regions = sorted(cleaned_df["region"].unique())
    all_stores  = sorted(cleaned_df["store_id"].unique())

    sel_cats    = st.multiselect("Category", all_cats,    default=all_cats)    or all_cats
    sel_regions = st.multiselect("Region",   all_regions, default=all_regions) or all_regions
    sel_stores  = st.multiselect("Store",    all_stores,  default=all_stores)  or all_stores

    n_days = (max_d - min_d).days + 1
    st.markdown(f"""
    <div class="sidebar-stats">
      <div class="stat-row"><span class="stat-key">Date range</span>
        <span class="stat-val">{min_d.strftime('%d %b %y')} – {max_d.strftime('%d %b %y')}</span></div>
      <div class="stat-row"><span class="stat-key">Total days</span>
        <span class="stat-val">{n_days:,}</span></div>
      <div class="stat-row"><span class="stat-key">Products</span>
        <span class="stat-val">{cleaned_df['product_id'].nunique()}</span></div>
      <div class="stat-row"><span class="stat-key">Stores</span>
        <span class="stat-val">{cleaned_df['store_id'].nunique()}</span></div>
      <div class="stat-row"><span class="stat-key">Categories</span>
        <span class="stat-val">{cleaned_df['category'].nunique()}</span></div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
fdf = cleaned_df[
    (cleaned_df["date"].dt.date >= start_d) &
    (cleaned_df["date"].dt.date <= end_d)   &
    (cleaned_df["category"].isin(sel_cats))  &
    (cleaned_df["region"].isin(sel_regions)) &
    (cleaned_df["store_id"].isin(sel_stores))
].copy()
ffc  = forecast_df[forecast_df["category"].isin(sel_cats)].copy()
frec = recom_df[recom_df["category"].isin(sel_cats)].copy()


# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
ref_date   = (forecast_df["reference_date"].iloc[0]
              if "reference_date" in forecast_df.columns else str(max_d))
n_products = fdf["product_id"].nunique()

st.markdown(f"""
<div class="page-hero">
  <div class="hero-eyebrow">Live · Inventory Intelligence Platform</div>
  <div class="hero-title">Smart Inventory<br><span>Replenishment Dashboard</span></div>
  <div class="hero-subtitle">
    AI-assisted demand forecasting and inventory risk analysis
    for smarter, faster stock replenishment decisions.
  </div>
  <div class="hero-meta">
    <div class="hero-meta-item"><div class="dot"></div>Reference date: {ref_date}</div>
    <div class="hero-meta-item"><div class="dot"></div>{n_products} active SKUs monitored</div>
    <div class="hero-meta-item"><div class="dot"></div>Forecast: Weighted Moving Average</div>
    <div class="hero-meta-item"><div class="dot"></div>{len(sel_stores)} store(s) · {len(sel_regions)} region(s)</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# §1  EXECUTIVE OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-wrap">
  <div class="section-rule"><span class="section-num">01</span><span class="section-line"></span></div>
  <div class="section-heading">Executive Overview</div>
  <div class="section-desc">Portfolio-wide KPIs for the active filter set</div>
</div>
""", unsafe_allow_html=True)

total_rev   = fdf["sales_revenue"].sum()
total_pft   = fdf["profit"].sum()
total_units = fdf["units_sold"].sum()
avg_margin  = fdf["profit_margin"].mean()
sc          = frec["inventory_status"].value_counts()
n_critical  = sc.get("Critical Stock", 0)
n_reorder   = sc.get("Reorder Soon",   0)
n_overstock = sc.get("Overstocked",    0)

def kpi_card(label, value, sub, color, alert_class=""):
    return (f"<div class='kpi-card' style='--kpi-color:{color}'>"
            f"<div class='kpi-label'>{label}</div>"
            f"<div class='kpi-value {alert_class}'>{value}</div>"
            f"<div class='kpi-sub'>{sub}</div></div>")

kpi_html = "<div class='kpi-grid'>"
kpi_html += kpi_card("Total Revenue",  f"£{total_rev/1e6:.2f}M", f"Avg margin {avg_margin:.1f}%", "#00D4FF")
kpi_html += kpi_card("Total Profit",   f"£{total_pft/1e6:.2f}M", "Net of COGS",                  "#00E5A0")
kpi_html += kpi_card("Units Sold",     f"{total_units/1e3:.0f}K", "across all stores",            "#A78BFA")
kpi_html += kpi_card("Active SKUs",    str(n_products),           "products monitored",           "#38BDF8")
kpi_html += kpi_card("Critical Stock", str(n_critical),           "below safety stock",           "#FF4D6D",
                     "kpi-alert" if n_critical else "kpi-ok")
kpi_html += kpi_card("Reorder Soon",   str(n_reorder),            "inside reorder point",         "#FFB547",
                     "kpi-warn" if n_reorder else "kpi-ok")
kpi_html += kpi_card("Overstocked",    str(n_overstock),          "excess stock on hand",         "#A78BFA",
                     "kpi-warn" if n_overstock else "kpi-ok")
kpi_html += "</div>"
st.markdown(kpi_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# §2  SALES PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-wrap">
  <div class="section-rule"><span class="section-num">02</span><span class="section-line"></span></div>
  <div class="section-heading">Sales Performance</div>
  <div class="section-desc">Revenue trends, category breakdown, and top-performing products</div>
</div>
""", unsafe_allow_html=True)

# Monthly revenue trend
monthly = (fdf.groupby(["year","month","month_name"])["sales_revenue"]
           .sum().reset_index().sort_values(["year","month"]))
monthly["period"] = monthly["month_name"].str[:3] + " " + monthly["year"].astype(str)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=monthly["period"], y=monthly["sales_revenue"],
    mode="lines+markers", name="Monthly Revenue",
    line=dict(color="#00D4FF", width=2),
    marker=dict(color="#00D4FF", size=5, line=dict(color="#030712", width=1.5)),
    fill="tozeroy", fillcolor="rgba(0,212,255,0.05)",
    hovertemplate="<b>%{x}</b><br>£%{y:,.0f}<extra></extra>",
))
themed(fig_trend)
chart_label("Monthly Revenue Trend")
st.plotly_chart(fig_trend, width="stretch")

col1, col2 = st.columns(2, gap="medium")
with col1:
    cat_rev = (fdf.groupby("category")["sales_revenue"].sum()
               .reset_index().sort_values("sales_revenue", ascending=True))
    n = len(cat_rev)
    fig_cat = px.bar(cat_rev, x="sales_revenue", y="category", orientation="h",
                     labels={"sales_revenue":"Revenue (£)","category":""})
    fig_cat.update_traces(
        marker_color=[f"rgba(0,212,255,{0.35+0.65*i/max(n-1,1)})" for i in range(n)],
        hovertemplate="<b>%{y}</b><br>£%{x:,.0f}<extra></extra>",
    )
    themed(fig_cat)
    fig_cat.update_layout(showlegend=False)
    chart_label("Revenue by Category")
    st.plotly_chart(fig_cat, width="stretch")

with col2:
    top10_rev = (fdf.groupby("product_name")["sales_revenue"].sum()
                 .reset_index().sort_values("sales_revenue", ascending=True).tail(10))
    n = len(top10_rev)
    fig_p10 = px.bar(top10_rev, x="sales_revenue", y="product_name", orientation="h",
                     labels={"sales_revenue":"Revenue (£)","product_name":""})
    fig_p10.update_traces(
        marker_color=[f"rgba(0,229,160,{0.35+0.65*i/max(n-1,1)})" for i in range(n)],
        hovertemplate="<b>%{y}</b><br>£%{x:,.0f}<extra></extra>",
    )
    themed(fig_p10)
    fig_p10.update_layout(showlegend=False)
    chart_label("Top 10 Products — Revenue")
    st.plotly_chart(fig_p10, width="stretch")

top10_u = (fdf.groupby("product_name")["units_sold"].sum()
           .reset_index().sort_values("units_sold", ascending=True).tail(10))
n = len(top10_u)
fig_units = px.bar(top10_u, x="units_sold", y="product_name", orientation="h",
                   labels={"units_sold":"Units Sold","product_name":""})
fig_units.update_traces(
    marker_color=[f"rgba(167,139,250,{0.35+0.65*i/max(n-1,1)})" for i in range(n)],
    hovertemplate="<b>%{y}</b><br>%{x:,.0f} units<extra></extra>",
)
themed(fig_units)
fig_units.update_layout(showlegend=False)
chart_label("Top 10 Products — Units Sold")
st.plotly_chart(fig_units, width="stretch")


# ─────────────────────────────────────────────────────────────────────────────
# §3  DEMAND FORECASTING
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-wrap">
  <div class="section-rule"><span class="section-num">03</span><span class="section-line"></span></div>
  <div class="section-heading">Demand Forecasting</div>
  <div class="section-desc">
    Weighted moving-average forecasts per product
    &nbsp;·&nbsp; 50% × 7-day &nbsp;+&nbsp; 30% × 14-day &nbsp;+&nbsp; 20% × 30-day
  </div>
</div>
""", unsafe_allow_html=True)

available_products = (sorted(ffc["product_name"].unique()) if not ffc.empty
                      else sorted(forecast_df["product_name"].unique()))
selected_product   = st.selectbox("Select Product", options=available_products)
fc_row             = forecast_df[forecast_df["product_name"] == selected_product].iloc[0]

prod_daily = (fdf[fdf["product_name"] == selected_product]
              .groupby("date")["units_sold"].sum()
              .reset_index().sort_values("date"))

# History + moving averages chart
fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(
    x=prod_daily["date"], y=prod_daily["units_sold"],
    mode="lines", name="Daily Demand",
    line=dict(color="rgba(0,212,255,0.35)", width=1),
    hovertemplate="%{x|%d %b %Y}<br><b>%{y} units</b><extra></extra>",
))
if len(prod_daily) >= 7:
    prod_daily["ma30"] = prod_daily["units_sold"].rolling(30, min_periods=1).mean()
    prod_daily["ma7"]  = prod_daily["units_sold"].rolling(7,  min_periods=1).mean()
    fig_hist.add_trace(go.Scatter(
        x=prod_daily["date"], y=prod_daily["ma30"], mode="lines", name="30-Day MA",
        line=dict(color="#FFB547", width=2, dash="dot"),
        hovertemplate="%{x|%d %b %Y}<br>30d MA: <b>%{y:.0f}</b><extra></extra>",
    ))
    fig_hist.add_trace(go.Scatter(
        x=prod_daily["date"], y=prod_daily["ma7"], mode="lines", name="7-Day MA",
        line=dict(color="#00E5A0", width=1.5),
        hovertemplate="%{x|%d %b %Y}<br>7d MA: <b>%{y:.0f}</b><extra></extra>",
    ))
themed(fig_hist)
chart_label(f"Daily Demand History · {selected_product}")
st.plotly_chart(fig_hist, width="stretch")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Avg Daily Demand",   f"{fc_row['avg_daily_demand']:,.0f} units")
m2.metric("Forecast — 7 Days",  f"{fc_row['forecast_next_7d']:,.0f} units")
m3.metric("Forecast — 14 Days", f"{fc_row['forecast_next_14d']:,.0f} units")
m4.metric("Forecast — 30 Days", f"{fc_row['forecast_next_30d']:,.0f} units")

st.markdown("<br>", unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap="medium")
with col_a:
    hz = pd.DataFrame({
        "Horizon": ["Next 7 Days","Next 14 Days","Next 30 Days"],
        "Units":   [fc_row["forecast_next_7d"], fc_row["forecast_next_14d"],
                    fc_row["forecast_next_30d"]],
    })
    fig_hz = px.bar(hz, x="Horizon", y="Units", color="Horizon",
                    color_discrete_map={"Next 7 Days":"#00D4FF",
                                        "Next 14 Days":"#FFB547","Next 30 Days":"#FF4D6D"},
                    text="Units", labels={"Units":"Forecasted Units"})
    fig_hz.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                         hovertemplate="<b>%{x}</b><br>%{y:,.0f} units<extra></extra>")
    themed(fig_hz)
    fig_hz.update_layout(showlegend=False)
    chart_label(f"Forecast by Horizon · {selected_product}")
    st.plotly_chart(fig_hz, width="stretch")

with col_b:
    ma_df = pd.DataFrame({
        "Window": ["7-Day Avg","14-Day Avg","30-Day Avg","Overall Avg"],
        "Units/Day": [fc_row["avg_demand_last_7d"], fc_row["avg_demand_last_14d"],
                      fc_row["avg_demand_last_30d"], fc_row["avg_daily_demand"]],
    })
    fig_ma = px.bar(ma_df, x="Window", y="Units/Day", color="Window",
                    color_discrete_sequence=["#00D4FF","#00E5A0","#FFB547","#A78BFA"],
                    text="Units/Day", labels={"Units/Day":"Units / Day"})
    fig_ma.update_traces(texttemplate="%{text:,.1f}", textposition="outside",
                         hovertemplate="<b>%{x}</b><br>%{y:.1f} units/day<extra></extra>")
    themed(fig_ma)
    fig_ma.update_layout(showlegend=False)
    chart_label(f"Moving Average Comparison · {selected_product}")
    st.plotly_chart(fig_ma, width="stretch")

st.markdown("<br>", unsafe_allow_html=True)
chart_label("Full Forecast Table — All Products")
fc_display = ffc[[
    "product_name","category","avg_daily_demand","std_daily_demand",
    "avg_demand_last_7d","avg_demand_last_14d","avg_demand_last_30d",
    "forecast_next_7d","forecast_next_14d","forecast_next_30d",
    "demand_variability","current_stock",
]].copy()
fc_display.columns = ["Product","Category","Avg/Day","Std Dev","Last 7d","Last 14d",
                       "Last 30d","Fcast 7d","Fcast 14d","Fcast 30d","Variability","Stock"]
st.dataframe(fc_display.sort_values("Fcast 30d", ascending=False),
             width="stretch", hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# §4  INVENTORY RISK
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-wrap">
  <div class="section-rule"><span class="section-num">04</span><span class="section-line"></span></div>
  <div class="section-heading">Inventory Risk</div>
  <div class="section-desc">Status classification, reorder thresholds, and suggested actions</div>
</div>
""", unsafe_allow_html=True)

STATUS_COLORS = {"Critical Stock":"#FF4D6D","Reorder Soon":"#FFB547",
                 "Healthy Stock":"#00E5A0","Overstocked":"#A78BFA","Slow Moving":"#00D4FF"}

col_l, col_r = st.columns([1, 1.8], gap="medium")
with col_l:
    sc_df = frec["inventory_status"].value_counts().reset_index()
    sc_df.columns = ["Status","Count"]
    sc_df["Color"] = sc_df["Status"].map(STATUS_COLORS)
    fig_donut = go.Figure(go.Pie(
        labels=sc_df["Status"], values=sc_df["Count"], hole=0.65,
        marker=dict(colors=sc_df["Color"], line=dict(color="#060B18", width=2)),
        hovertemplate="<b>%{label}</b><br>%{value} SKUs (%{percent})<extra></extra>",
        textinfo="percent", textfont=dict(color="#F0F6FF", size=10, family=_FONT),
        direction="clockwise", sort=True,
    ))
    fig_donut.add_annotation(text=f"<b>{len(frec)}</b>", x=0.5, y=0.55,
                              showarrow=False, font=dict(color="#F0F6FF", size=22, family=_FONT))
    fig_donut.add_annotation(text="SKUs", x=0.5, y=0.38,
                              showarrow=False, font=dict(color="#4A6080", size=11, family=_FONT))
    themed(fig_donut)
    # Use layout.legend.update() to avoid duplicate 'legend' key conflict with THEME
    fig_donut.layout.legend.update(orientation="v", x=1, y=0.5,
                                   font=dict(color="#8BA3C7", size=10))
    chart_label("Status Distribution")
    st.plotly_chart(fig_donut, width="stretch")

with col_r:
    top_rq = (frec[frec["suggested_reorder_qty"] > 0]
              .sort_values("suggested_reorder_qty", ascending=True).tail(15))
    fig_rq = px.bar(top_rq, x="suggested_reorder_qty", y="product_name", orientation="h",
                    color="reorder_priority",
                    color_discrete_map={"High":"#FF4D6D","Medium":"#FFB547","Low":"#00E5A0"},
                    labels={"suggested_reorder_qty":"Units to Order","product_name":""})
    fig_rq.update_traces(hovertemplate="<b>%{y}</b><br>Order: %{x:,.0f} units<extra></extra>")
    themed(fig_rq)
    chart_label("Suggested Reorder Quantities — Top 15 Products")
    st.plotly_chart(fig_rq, width="stretch")

def clean_table(df_sub):
    keep = ["product_name","category","current_stock","safety_stock_units",
            "reorder_point_units","forecast_next_30d","suggested_reorder_qty",
            "estimated_order_value","inventory_status","reorder_priority",
            "days_of_stock_remaining"]
    keep = [c for c in keep if c in df_sub.columns]
    out  = df_sub[keep].copy()
    out.columns = [c.replace("_"," ").title() for c in keep]
    return out.reset_index(drop=True)

tabs = st.tabs([
    "🔴 Critical",
    "🟡 Reorder Soon",
    "🟣 Overstocked",
    "🔵 Slow Moving",
    "📋 All Products"
])

with tabs[0]:
    crit = frec[frec["inventory_status"] == "Critical Stock"]

    if crit.empty:
        st.success("✅ No products in Critical Stock status.")
    else:
        st.error(f"**{len(crit)} product(s) below safety stock — immediate action required.**")
        st.dataframe(
            clean_table(crit),
            width="stretch",
            hide_index=True
        )

with tabs[1]:
    rsn = frec[frec["inventory_status"] == "Reorder Soon"]

    if rsn.empty:
        st.success("✅ No products approaching reorder point.")
    else:
        st.warning(f"**{len(rsn)} product(s) below their reorder point.**")
        st.dataframe(
            clean_table(rsn.sort_values("days_of_stock_remaining")),
            width="stretch",
            hide_index=True
        )

with tabs[2]:
    ovr = frec[frec["inventory_status"] == "Overstocked"]

    if ovr.empty:
        st.success("✅ No overstocked products.")
    else:
        st.info(f"**{len(ovr)} product(s) exceed 1.5× the 30-day demand forecast.**")
        st.dataframe(
            clean_table(ovr),
            width="stretch",
            hide_index=True
        )

with tabs[3]:
    slw = frec[frec["inventory_status"] == "Slow Moving"]

    if slw.empty:
        st.info("No slow-moving products in current filter.")
    else:
        st.info(f"**{len(slw)} product(s) in the bottom 20% of daily demand.**")
        st.dataframe(
            clean_table(slw),
            width="stretch",
            hide_index=True
        )

with tabs[4]:
    priority_order = {"High": 0, "Medium": 1, "Low": 2}

    all_products_table = frec.copy()
    all_products_table["priority_sort"] = all_products_table["reorder_priority"].map(priority_order)

    all_products_table = all_products_table.sort_values(
        ["priority_sort", "suggested_reorder_qty"],
        ascending=[True, False]
    )

    st.dataframe(
        clean_table(all_products_table),
        width="stretch",
        hide_index=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# §5  BUSINESS INSIGHT SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-wrap">
  <div class="section-rule"><span class="section-num">05</span><span class="section-line"></span></div>
  <div class="section-heading">Business Insight Summary</div>
  <div class="section-desc">Rule-based plain-English intelligence — derived entirely from data, no external API</div>
</div>
""", unsafe_allow_html=True)

def generate_insights(sales_df, fc_df, rec_df):
    """Generate list of {label, color, text} insight dicts from data."""
    ins = []
    n_crit  = (rec_df["inventory_status"] == "Critical Stock").sum()
    n_reord = (rec_df["inventory_status"] == "Reorder Soon").sum()

    # 1 — Stock health
    if n_crit > 0:
        ins.append(dict(label="Urgent Action Required", color="#FF4D6D", text=(
            f"<b>{n_crit} product(s)</b> are below their safety stock threshold and face "
            f"immediate stockout risk. An additional <b>{n_reord} SKU(s)</b> are approaching "
            f"their reorder point. Place replenishment orders for all {n_crit+n_reord} at-risk "
            f"SKUs before the next delivery window closes."
        )))
    elif n_reord > 0:
        ins.append(dict(label="Reorder Attention", color="#FFB547", text=(
            f"No products are critical, but <b>{n_reord} SKU(s)</b> have stock levels below "
            f"their calculated reorder point. Schedule procurement within the next lead-time "
            f"window to prevent future stockouts."
        )))
    else:
        ins.append(dict(label="Stock Health — All Clear", color="#00E5A0", text=(
            "All products maintain stock levels above their reorder points. "
            "Continue monitoring daily demand movements, especially for seasonal SKUs."
        )))

    # 2 — Risk concentration by category
    risk_rows = rec_df[rec_df["inventory_status"].isin(["Critical Stock","Reorder Soon"])]
    if not risk_rows.empty and "category" in risk_rows.columns:
        top_cat = risk_rows["category"].value_counts().idxmax()
        top_n   = risk_rows["category"].value_counts().max()
        ins.append(dict(label="Risk Concentration", color="#FFB547", text=(
            f"Most inventory risk is concentrated in <b>{top_cat}</b>, which accounts for "
            f"<b>{top_n}</b> of the at-risk SKUs. Review supplier lead times and reorder "
            f"policies for this category to reduce systemic exposure."
        )))

    # 3 — Revenue trend
    if len(sales_df) > 0:
        _s = sales_df.copy()
        _s["ym"] = _s["date"].dt.to_period("M")
        mrev = _s.groupby("ym")["sales_revenue"].sum().sort_index()
        if len(mrev) >= 2:
            last, prev = mrev.iloc[-1], mrev.iloc[-2]
            pct = ((last - prev) / prev * 100) if prev else 0
            up  = pct >= 0
            ins.append(dict(
                label=f"Revenue Trend · {'+' if up else ''}{pct:.1f}%",
                color="#00E5A0" if up else "#FF4D6D",
                text=(
                    f"Revenue <b>{'increased' if up else 'decreased'} by {abs(pct):.1f}%</b> "
                    f"in the most recent full month (£{last:,.0f} vs £{prev:,.0f}). "
                    + ("Sustain momentum by keeping top-selling SKUs in stock."
                       if up else "Investigate stockouts or demand shifts that may have driven this decline.")
                )
            ))

    # 4 — Top revenue driver
    if not sales_df.empty:
        grp      = sales_df.groupby("product_name")["sales_revenue"].sum()
        top_name = grp.idxmax()
        top_val  = grp.max()
        top_pct  = top_val / sales_df["sales_revenue"].sum() * 100
        ins.append(dict(label="Top Revenue Driver", color="#00D4FF", text=(
            f"<b>{top_name}</b> is the highest-revenue SKU, contributing "
            f"<b>£{top_val:,.0f}</b> ({top_pct:.1f}% of total filtered revenue). "
            f"A single day out-of-stock represents a significant revenue impact — "
            f"ensure this product always sits above its reorder point."
        )))

    # 5 — Overstock
    n_over = (rec_df["inventory_status"] == "Overstocked").sum()
    if n_over > 0:
        ins.append(dict(label="Overstock Opportunity", color="#A78BFA", text=(
            f"<b>{n_over} product(s)</b> carry more than 1.5× their 30-day demand forecast. "
            f"Consider targeted promotions, inter-store stock redistribution, or reduced "
            f"next-order quantities to free working capital and lower holding costs."
        )))

    # 6 — Slow movers
    n_slow = (rec_df["inventory_status"] == "Slow Moving").sum()
    if n_slow > 0:
        names   = rec_df[rec_df["inventory_status"]=="Slow Moving"]["product_name"].tolist()
        preview = ", ".join(names[:3]) + (f" and {n_slow-3} others" if n_slow > 3 else "")
        ins.append(dict(label="Slow-Moving SKUs", color="#38BDF8", text=(
            f"<b>{n_slow} SKU(s)</b> fall in the bottom 20% of daily demand: "
            f"<b>{preview}</b>. Review shelf-space allocation, order frequency, "
            f"and whether supplier minimums can be renegotiated."
        )))

    # 7 — Margin analysis
    if "profit_margin" in sales_df.columns and not sales_df.empty:
        avg_m = sales_df["profit_margin"].mean()
        cat_m = sales_df.groupby("category")["profit_margin"].mean()
        ins.append(dict(label="Margin Analysis", color="#00E5A0", text=(
            f"Overall average profit margin is <b>{avg_m:.1f}%</b>. "
            f"<b>{cat_m.idxmax()}</b> leads at {cat_m.max():.1f}% while "
            f"<b>{cat_m.idxmin()}</b> trails at {cat_m.min():.1f}%. "
            f"Prioritise replenishment for high-margin categories to maximise "
            f"return on inventory investment."
        )))

    # 8 — Procurement total
    total_val = rec_df["estimated_order_value"].sum()
    n_orders  = (rec_df["suggested_reorder_qty"] > 0).sum()
    ins.append(dict(label="Procurement Summary", color="#FFB547", text=(
        f"<b>{n_orders} products</b> require replenishment with a combined estimated "
        f"procurement value of <b>£{total_val:,.0f}</b>. Prioritise High-priority orders "
        f"first to prevent revenue-impacting stockouts while managing cash flow exposure."
    )))

    return ins

insights = generate_insights(fdf, ffc, frec)
st.markdown("<div class='insights-grid'>", unsafe_allow_html=True)
for ins in insights:
    ic_color = ins["color"]
    ic_label = ins["label"]
    ic_text  = ins["text"]
    st.markdown(
        f"<div class='insight-card' style='--ic-color:{ic_color}'>"
        f"<div class='insight-tag'><div class='ic-dot'></div>{ic_label}</div>"
        f"<div class='insight-body'>{ic_text}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-footer">
  <div class="footer-left">
    <span class="footer-pill"><span class="fp-dot"></span>Streamlit</span>
    <span class="footer-pill"><span class="fp-dot"></span>Plotly</span>
    <span class="footer-pill"><span class="fp-dot"></span>Pandas · NumPy</span>
    <span class="footer-pill"><span class="fp-dot"></span>Python 3.10+</span>
  </div>
  <div class="footer-right">
    ◈ INVIQ · Smart Inventory Replenishment Dashboard
    &nbsp;&nbsp;·&nbsp;&nbsp;Forecast: WMA (50% 7d · 30% 14d · 20% 30d)
  </div>
</div>
""", unsafe_allow_html=True)
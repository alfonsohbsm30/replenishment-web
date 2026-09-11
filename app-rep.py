"""
Global Inventory & Replenishment Analytics
============================================
Dashboard analisis inventory & replenishment ala SCM/Inventory Analyst,
dilengkapi data sintetis global (multi-region, multi-kategori, multi-SKU).

UI/UX terinspirasi dari template Excel "Inventory Management System":
header banner biru navy tegas, kartu KPI berwarna solid (navy/teal/oranye/merah),
banner peringatan kuning untuk item kritis, badge status berwarna, dan tabel bersih.

Cara jalankan:
    pip install streamlit pandas numpy plotly
    streamlit run app-rep.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# -----------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Global Inventory & Replenishment Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------
# DESIGN TOKENS (diselaraskan dengan template Excel "Inventory Management")
# -----------------------------------------------------------------------
NAVY_DARK = "#16233F"     # header utama & footer
NAVY = "#1E3A5F"          # kartu KPI netral / header tabel
ACCENT_BLUE = "#2E75B6"   # garis aksen tipis
TEAL = "#127C63"          # kartu KPI "nilai / sehat"
ORANGE = "#C1770F"        # kartu KPI "peringatan" & badge Medium/High
RED = "#C0392B"           # kartu KPI "kritis" & badge Critical
BG_PAGE = "#F3F5F9"       # latar halaman
BG_CARD = "#FFFFFF"       # latar card/table
BANNER_BG = "#FCEFC7"     # banner peringatan kuning
BANNER_TEXT = "#7A5300"
TEXT_MUTED = "#5B6472"

# -----------------------------------------------------------------------
# STYLING
# -----------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}

    .stApp {{
        background-color: {BG_PAGE};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {NAVY_DARK};
    }}
    section[data-testid="stSidebar"] * {{
        color: #E8ECF3 !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15);
    }}
    /* Alert box (success/error) di sidebar butuh kontras sendiri, jangan ikut ditimpa */
    section[data-testid="stSidebar"] div[data-testid="stAlert"] {{
        background-color: rgba(255,255,255,0.92) !important;
        border-radius: 8px;
    }}
    section[data-testid="stSidebar"] div[data-testid="stAlert"] p,
    section[data-testid="stSidebar"] div[data-testid="stAlert"] span,
    section[data-testid="stSidebar"] div[data-testid="stAlert"] div {{
        color: {NAVY_DARK} !important;
    }}

    /* Hero header banner */
    .app-header {{
        background: linear-gradient(90deg, {NAVY_DARK} 0%, {NAVY} 100%);
        border-radius: 10px;
        padding: 28px 32px 22px 32px;
        margin-bottom: 4px;
    }}
    .app-header h1 {{
        color: #FFFFFF;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.2px;
    }}
    .app-header p {{
        color: #C9D4E3;
        margin: 6px 0 0 0;
        font-size: 0.95rem;
    }}
    .app-header-accent {{
        height: 5px;
        background: {ACCENT_BLUE};
        border-radius: 0 0 6px 6px;
        margin-bottom: 22px;
    }}

    /* KPI cards */
    .kpi-card {{
        border-radius: 10px;
        padding: 16px 18px;
        color: #FFFFFF;
        height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(16,25,46,0.12);
    }}
    .kpi-label {{
        font-size: 0.78rem;
        font-weight: 600;
        opacity: 0.9;
        text-transform: none;
        margin-bottom: 4px;
    }}
    .kpi-value {{
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.1;
    }}
    .kpi-sub {{
        font-size: 0.72rem;
        opacity: 0.85;
        margin-top: 3px;
    }}

    /* Alert banner */
    .alert-banner {{
        background-color: {BANNER_BG};
        color: {BANNER_TEXT};
        border-left: 5px solid {ORANGE};
        border-radius: 8px;
        padding: 12px 18px;
        font-weight: 700;
        font-size: 0.95rem;
        margin: 6px 0 16px 0;
    }}

    /* Section card wrapper */
    .section-card {{
        background-color: {BG_CARD};
        border: 1px solid #E3E7EE;
        border-radius: 10px;
        padding: 18px 20px 8px 20px;
        margin-bottom: 18px;
    }}
    .section-title {{
        font-size: 1rem;
        font-weight: 700;
        color: {NAVY_DARK};
        margin-bottom: 10px;
    }}

    /* Tabel HTML mentah (pandas Styler .to_html) di dalam section-card */
    .section-card table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
    }}
    .section-card table th {{
        background-color: {NAVY} !important;
        color: #FFFFFF !important;
        padding: 8px 10px;
        text-align: left;
        position: sticky;
        top: 0;
    }}
    .section-card table td {{
        padding: 7px 10px;
        color: {NAVY_DARK} !important;
        border-bottom: 1px solid #E3E7EE;
        background-color: {BG_CARD};
    }}
    .section-card table tr:nth-child(even) td {{
        background-color: #F7F9FC;
    }}

    /* Status badges */
    .badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        min-width: 64px;
    }}
    .badge-critical {{ background-color: {RED}; }}
    .badge-high {{ background-color: {ORANGE}; }}
    .badge-medium {{ background-color: #D8A32B; }}
    .badge-low {{ background-color: {TEAL}; }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{gap: 4px;}}
    .stTabs [data-baseweb="tab"] {{
        background-color: #E8ECF3;
        border-radius: 8px 8px 0 0;
        padding: 8px 18px;
        font-weight: 600;
        color: {NAVY_DARK};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {NAVY} !important;
        color: #FFFFFF !important;
    }}

    /* Dataframe header */
    div[data-testid="stDataFrame"] thead tr th {{
        background-color: {NAVY} !important;
        color: #FFFFFF !important;
    }}

    /* Footer */
    .app-footer {{
        background-color: {NAVY_DARK};
        color: #AEB9C9;
        font-style: italic;
        font-size: 0.8rem;
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        margin-top: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi_card(label: str, value: str, color: str, sub: str = "") -> str:
    """Render satu kartu KPI bergaya solid seperti template Excel."""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card" style="background-color:{color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>
    """


def risk_badge(risk: str) -> str:
    cls_map = {
        "Critical": "badge-critical",
        "High": "badge-high",
        "Medium": "badge-medium",
        "Low": "badge-low",
    }
    return f'<span class="badge {cls_map.get(risk, "badge-low")}">{risk}</span>'


# -----------------------------------------------------------------------
# SUMBER DATA: GOOGLE SHEET (live "database") + fallback data sintetis
# -----------------------------------------------------------------------
# Ganti dua nilai ini sesuai Google Sheet kamu:
#   SHEET_ID -> bagian ".../d/<SHEET_ID>/edit..." pada URL Google Sheet
#   SHEET_GID -> id tab/sheet (lihat "gid=..." pada URL saat tab dibuka)
# Sheet WAJIB di-share "Anyone with the link -> Viewer" agar bisa dibaca.
SHEET_ID = "16Txk46U1WRGtLCuuO-cZ4-ZDtQFYk7gYrXvpqk7Dq28"
SHEET_GID = "0"  # ganti dengan gid tab "RawData" milikmu

RAW_COLUMNS = {
    "SKU ID": "sku_id",
    "Region": "region",
    "Country": "country",
    "Category": "category",
    "Item": "item",
    "Supplier": "supplier",
    "Lead Time (days)": "lead_time_days",
    "Daily Demand Avg": "daily_demand_avg",
    "Demand Std Dev": "demand_std",
    "Service Level (Z)": "service_level_z",
    "On Hand Qty": "on_hand_qty",
    "Unit Cost (USD)": "unit_cost",
    "MOQ": "moq",
    "Lot Size": "lot_size",
    "Open PO Qty": "open_po_qty",
}


def compute_derived_metrics(raw: pd.DataFrame) -> pd.DataFrame:
    """Hitung safety stock, ROP, stockout risk, ABC class, dll dari kolom mentah."""
    df = raw.copy()

    numeric_cols = [
        "lead_time_days", "daily_demand_avg", "demand_std", "service_level_z",
        "on_hand_qty", "unit_cost", "moq", "lot_size", "open_po_qty",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=numeric_cols).reset_index(drop=True)

    df["safety_stock"] = round(df["service_level_z"] * df["demand_std"] * np.sqrt(df["lead_time_days"]), 0)
    df["reorder_point"] = round(df["daily_demand_avg"] * df["lead_time_days"] + df["safety_stock"], 0)
    df["days_of_supply"] = np.where(
        df["daily_demand_avg"] > 0, round(df["on_hand_qty"] / df["daily_demand_avg"], 1), 0
    )
    df["abc_value"] = df["daily_demand_avg"] * df["unit_cost"]

    df["inventory_position"] = df["on_hand_qty"] + df["open_po_qty"]
    df["below_rop"] = df["inventory_position"] < df["reorder_point"]
    df["suggested_order_qty"] = np.where(
        df["below_rop"],
        np.maximum(df["moq"], np.ceil((df["reorder_point"] * 1.5 - df["inventory_position"]) / df["lot_size"]) * df["lot_size"]),
        0,
    )
    df["stockout_risk"] = np.select(
        [df["days_of_supply"] < 5, df["days_of_supply"] < 14, df["days_of_supply"] < 30],
        ["Critical", "High", "Medium"],
        default="Low",
    )
    df["inventory_value"] = df["on_hand_qty"] * df["unit_cost"]

    df = df.sort_values("abc_value", ascending=False).reset_index(drop=True)
    df["cum_pct"] = df["abc_value"].cumsum() / df["abc_value"].sum()
    df["abc_class"] = np.select(
        [df["cum_pct"] <= 0.8, df["cum_pct"] <= 0.95],
        ["A", "B"],
        default="C",
    )
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_data_from_gsheet(sheet_id: str, gid: str) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    raw = pd.read_csv(url)
    raw = raw.rename(columns={k: v for k, v in RAW_COLUMNS.items() if k in raw.columns})
    missing = set(RAW_COLUMNS.values()) - set(raw.columns)
    if missing:
        raise ValueError(f"Kolom hilang di Google Sheet: {', '.join(sorted(missing))}")
    return compute_derived_metrics(raw)


@st.cache_data
def generate_dummy_data(seed: int = 42) -> pd.DataFrame:
    """Fallback: data sintetis, dipakai kalau Google Sheet belum ter-setup/gagal diakses."""
    rng = np.random.default_rng(seed)

    regions = {
        "North America": ["USA", "Canada", "Mexico"],
        "Europe": ["Germany", "France", "Netherlands", "UK"],
        "Asia Pacific": ["Indonesia", "China", "Japan", "Australia"],
        "Latin America": ["Brazil", "Chile"],
        "Middle East & Africa": ["UAE", "South Africa"],
    }
    categories = {
        "Electronics": ["Smartphone Case", "USB-C Cable", "Bluetooth Speaker", "Power Bank"],
        "Apparel": ["Cotton T-Shirt", "Running Shoes", "Denim Jacket"],
        "Home & Living": ["LED Lamp", "Ceramic Mug", "Storage Box"],
        "Food & Beverage": ["Instant Coffee", "Energy Bar", "Mineral Water 1L"],
        "Industrial": ["Steel Bolt M8", "Hydraulic Hose", "Safety Gloves"],
    }
    suppliers = [f"Supplier-{c}" for c in ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]]

    rows = []
    sku_id = 1000
    for region, countries in regions.items():
        for country in countries:
            for category, items in categories.items():
                for item in items:
                    sku_id += 1
                    rows.append(dict(
                        sku_id=f"SKU-{sku_id}",
                        region=region,
                        country=country,
                        category=category,
                        item=item,
                        supplier=rng.choice(suppliers),
                        lead_time_days=int(rng.integers(5, 45)),
                        daily_demand_avg=round(rng.uniform(3, 120), 1),
                        demand_std=round(rng.uniform(1, 30), 1),
                        service_level_z=rng.choice([1.28, 1.65, 1.96, 2.05], p=[0.2, 0.4, 0.3, 0.1]),
                        on_hand_qty=round(rng.uniform(0, 3000), 0),
                        unit_cost=round(rng.uniform(1.5, 250), 2),
                        moq=int(rng.choice([50, 100, 200, 500, 1000])),
                        lot_size=int(rng.choice([100, 250, 500, 1000, 2000])),
                        open_po_qty=int(rng.choice([0, 0, 0, 100, 200])),
                    ))
    return compute_derived_metrics(pd.DataFrame(rows))


# -----------------------------------------------------------------------
# SIDEBAR: SUMBER DATA + FILTER
# -----------------------------------------------------------------------
st.sidebar.markdown("## 📦 Filter Data")
st.sidebar.caption("Global Inventory & Replenishment Dashboard")

data_source = st.sidebar.radio("Sumber Data", ["Google Sheet (Live)", "Data Dummy (Offline)"], index=0)

if data_source == "Google Sheet (Live)":
    try:
        df = load_data_from_gsheet(SHEET_ID, SHEET_GID)
        st.sidebar.success("Terhubung ke Google Sheet ✅")
    except Exception as e:
        st.sidebar.error(f"Gagal ambil data dari Google Sheet, pakai data dummy.\n\n{e}")
        df = generate_dummy_data()
else:
    df = generate_dummy_data()

if st.sidebar.button("🔄 Refresh Data"):
    load_data_from_gsheet.clear()
    st.rerun()

st.sidebar.markdown("---")

region_sel = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
category_sel = st.sidebar.multiselect("Kategori", sorted(df["category"].unique()), default=sorted(df["category"].unique()))
abc_sel = st.sidebar.multiselect("ABC Class", sorted(df["abc_class"].unique()), default=sorted(df["abc_class"].unique()))
risk_sel = st.sidebar.multiselect(
    "Stockout Risk",
    ["Critical", "High", "Medium", "Low"],
    default=["Critical", "High", "Medium", "Low"],
)

filtered = df[
    df["region"].isin(region_sel)
    & df["category"].isin(category_sel)
    & df["abc_class"].isin(abc_sel)
    & df["stockout_risk"].isin(risk_sel)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Menampilkan **{len(filtered):,}** dari **{len(df):,}** SKU")
st.sidebar.caption(
    "Data ditarik langsung dari Google Sheet (cache 5 menit)."
    if data_source == "Google Sheet (Live)"
    else "Mode data dummy — tidak terhubung ke Google Sheet."
)

# -----------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------
st.markdown(
    f"""
    <div class="app-header">
        <h1>📦 GLOBAL INVENTORY &amp; REPLENISHMENT DASHBOARD</h1>
        <p>Laporan per : {datetime.now().strftime("%d %B %Y")} &nbsp;|&nbsp; Ringkasan kesehatan inventory, sinyal replenishment, dan prioritas aksi lintas region &amp; kategori.</p>
    </div>
    <div class="app-header-accent"></div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------
# KPI CARDS
# -----------------------------------------------------------------------
total_value = filtered["inventory_value"].sum()
total_skus = filtered["sku_id"].nunique()
below_rop_count = filtered["below_rop"].sum()
critical_count = (filtered["stockout_risk"] == "Critical").sum()
avg_dos = filtered["days_of_supply"].mean() if len(filtered) else 0

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(kpi_card("TOTAL INVENTORY VALUE", f"${total_value:,.0f}", NAVY), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("TOTAL SKU AKTIF", f"{total_skus:,}", ACCENT_BLUE), unsafe_allow_html=True)
with k3:
    pct_rop = f"{below_rop_count/total_skus*100:.1f}% dari total" if total_skus else "0%"
    st.markdown(kpi_card("SKU DI BAWAH ROP", f"{below_rop_count:,}", ORANGE, pct_rop), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("SKU RISIKO CRITICAL", f"{critical_count:,}", RED), unsafe_allow_html=True)
with k5:
    st.markdown(kpi_card("RATA-RATA DAYS OF SUPPLY", f"{avg_dos:.1f} hari", TEAL), unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🌍 Overview Global", "🚨 Prioritas Replenishment", "📊 ABC & Kategori", "📋 Detail Data"]
)

# --- TAB 1: OVERVIEW ---
with tab1:
    colA, colB = st.columns([1.3, 1])

    with colA:
        region_summary = (
            filtered.groupby("region")
            .agg(inventory_value=("inventory_value", "sum"), sku_count=("sku_id", "nunique"))
            .reset_index()
            .sort_values("inventory_value", ascending=False)
        )
        fig_region = px.bar(
            region_summary,
            x="inventory_value",
            y="region",
            orientation="h",
            text_auto=".2s",
            title="Inventory Value per Region",
            color_discrete_sequence=[ACCENT_BLUE],
        )
        fig_region.update_traces(marker_color=ACCENT_BLUE)
        fig_region.update_layout(
            showlegend=False, height=380, plot_bgcolor="white", paper_bgcolor="white",
            font_color=NAVY_DARK, title_font_size=15,
        )
        st.plotly_chart(fig_region, use_container_width=True)

    with colB:
        risk_summary = filtered["stockout_risk"].value_counts().reindex(["Critical", "High", "Medium", "Low"]).fillna(0)
        fig_risk = px.pie(
            names=risk_summary.index,
            values=risk_summary.values,
            title="Distribusi Stockout Risk",
            color=risk_summary.index,
            color_discrete_map={"Critical": RED, "High": ORANGE, "Medium": "#D8A32B", "Low": TEAL},
            hole=0.5,
        )
        fig_risk.update_layout(height=380, paper_bgcolor="white", font_color=NAVY_DARK, title_font_size=15)
        st.plotly_chart(fig_risk, use_container_width=True)

    colC, colD = st.columns(2)
    with colC:
        country_summary = (
            filtered.groupby(["region", "country"])["inventory_value"].sum().reset_index()
        )
        fig_tree = px.treemap(
            country_summary,
            path=["region", "country"],
            values="inventory_value",
            title="Inventory Value: Region → Country",
            color="inventory_value",
            color_continuous_scale=[TEAL, NAVY],
        )
        fig_tree.update_layout(height=420, paper_bgcolor="white", font_color=NAVY_DARK, title_font_size=15)
        st.plotly_chart(fig_tree, use_container_width=True)

    with colD:
        dos_by_cat = filtered.groupby("category")["days_of_supply"].mean().reset_index().sort_values("days_of_supply")
        fig_dos = px.bar(
            dos_by_cat,
            x="days_of_supply",
            y="category",
            orientation="h",
            title="Rata-rata Days of Supply per Kategori",
            color="days_of_supply",
            color_continuous_scale=[RED, ORANGE, TEAL],
        )
        fig_dos.update_layout(height=420, coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white", font_color=NAVY_DARK, title_font_size=15)
        st.plotly_chart(fig_dos, use_container_width=True)

# --- TAB 2: REPLENISHMENT PRIORITY ---
with tab2:
    action_df = filtered[filtered["below_rop"]].copy()
    action_df = action_df.sort_values(["stockout_risk", "abc_class", "days_of_supply"])

    st.markdown(
        f"""<div class="alert-banner">⚠️ {len(action_df):,} SKU saat ini berada di bawah Reorder Point (ROP) dan memerlukan tindakan order segera.</div>""",
        unsafe_allow_html=True,
    )

    display_df = action_df.copy()
    display_df["Status"] = display_df["stockout_risk"].apply(risk_badge)
    display_cols_map = {
        "sku_id": "SKU",
        "item": "Item",
        "region": "Region",
        "country": "Country",
        "category": "Kategori",
        "supplier": "Supplier",
        "on_hand_qty": "On Hand",
        "open_po_qty": "Open PO",
        "reorder_point": "ROP",
        "days_of_supply": "Days of Supply",
        "Status": "Status",
        "abc_class": "ABC",
        "suggested_order_qty": "Suggested Order Qty",
        "unit_cost": "Unit Cost",
    }
    table_html = display_df[list(display_cols_map.keys())].rename(columns=display_cols_map)
    st.markdown('<div class="section-card"><div class="section-title">Daftar SKU yang Butuh Replenishment</div>', unsafe_allow_html=True)
    st.write(
        table_html.style.format(
            {
                "On Hand": "{:,.0f}",
                "Open PO": "{:,.0f}",
                "ROP": "{:,.0f}",
                "Days of Supply": "{:.1f}",
                "Suggested Order Qty": "{:,.0f}",
                "Unit Cost": "${:.2f}",
            }
        ).to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    colE, colF = st.columns(2)
    with colE:
        top_order_value = action_df.copy()
        top_order_value["order_value"] = top_order_value["suggested_order_qty"] * top_order_value["unit_cost"]
        top_order_value = top_order_value.sort_values("order_value", ascending=False).head(10)
        fig_order = px.bar(
            top_order_value,
            x="order_value",
            y="item",
            orientation="h",
            color="stockout_risk",
            color_discrete_map={"Critical": RED, "High": ORANGE, "Medium": "#D8A32B", "Low": TEAL},
            title="Top 10 Estimasi Nilai Order Replenishment",
        )
        fig_order.update_layout(height=420, yaxis={"categoryorder": "total ascending"}, plot_bgcolor="white", paper_bgcolor="white", font_color=NAVY_DARK, title_font_size=15)
        st.plotly_chart(fig_order, use_container_width=True)

    with colF:
        supplier_summary = (
            action_df.groupby("supplier")["suggested_order_qty"].sum().reset_index().sort_values("suggested_order_qty", ascending=False)
        )
        fig_supplier = px.bar(
            supplier_summary,
            x="suggested_order_qty",
            y="supplier",
            orientation="h",
            title="Total Suggested Order Qty per Supplier",
            color_discrete_sequence=[NAVY],
        )
        fig_supplier.update_traces(marker_color=NAVY)
        fig_supplier.update_layout(height=420, plot_bgcolor="white", paper_bgcolor="white", font_color=NAVY_DARK, title_font_size=15)
        st.plotly_chart(fig_supplier, use_container_width=True)

# --- TAB 3: ABC & CATEGORY ---
with tab3:
    colG, colH = st.columns(2)
    with colG:
        abc_summary = filtered.groupby("abc_class").agg(
            sku_count=("sku_id", "nunique"), inventory_value=("inventory_value", "sum")
        ).reset_index()
        fig_abc = px.bar(
            abc_summary,
            x="abc_class",
            y="inventory_value",
            text_auto=".2s",
            color="abc_class",
            color_discrete_map={"A": TEAL, "B": ORANGE, "C": RED},
            title="Inventory Value per ABC Class",
        )
        fig_abc.update_layout(height=400, showlegend=False, plot_bgcolor="white", paper_bgcolor="white", font_color=NAVY_DARK, title_font_size=15)
        st.plotly_chart(fig_abc, use_container_width=True)

    with colH:
        fig_scatter = px.scatter(
            filtered,
            x="daily_demand_avg",
            y="lead_time_days",
            size="inventory_value",
            color="abc_class",
            hover_name="item",
            color_discrete_map={"A": TEAL, "B": ORANGE, "C": RED},
            title="Demand vs Lead Time (bubble = inventory value)",
        )
        fig_scatter.update_layout(height=400, plot_bgcolor="white", paper_bgcolor="white", font_color=NAVY_DARK, title_font_size=15)
        st.plotly_chart(fig_scatter, use_container_width=True)

    cat_summary = (
        filtered.groupby("category")
        .agg(
            sku_count=("sku_id", "nunique"),
            inventory_value=("inventory_value", "sum"),
            avg_dos=("days_of_supply", "mean"),
            below_rop=("below_rop", "sum"),
        )
        .reset_index()
        .sort_values("inventory_value", ascending=False)
    )
    st.markdown('<div class="section-card"><div class="section-title">Ringkasan per Kategori</div>', unsafe_allow_html=True)
    st.dataframe(
        cat_summary.style.format(
            {"inventory_value": "${:,.0f}", "avg_dos": "{:.1f}"}
        ),
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 4: RAW DATA ---
with tab4:
    st.markdown('<div class="section-card"><div class="section-title">📋 Detail Seluruh SKU (sesuai filter)</div>', unsafe_allow_html=True)
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=550)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download data (CSV)", csv, "inventory_replenishment_data.csv", "text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="app-footer">
        Global Inventory &amp; Replenishment Dashboard &nbsp;|&nbsp; Data bersifat sintetis untuk ilustrasi analisis SCM/Inventory Management &nbsp;|&nbsp;
        ROP = (rata-rata demand harian × lead time) + safety stock &nbsp;|&nbsp; Safety stock = Z × σ_demand × √(lead time) &nbsp;|&nbsp; © 2026
    </div>
    """,
    unsafe_allow_html=True,
)

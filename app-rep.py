"""
Global Inventory & Replenishment Analytics
============================================
Dashboard analisis inventory & replenishment ala SCM/Inventory Analyst,
dilengkapi data sintetis global (multi-region, multi-kategori, multi-SKU).

Cara jalankan:
    pip install streamlit pandas numpy plotly
    streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
# STYLING
# -----------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main {background-color: #0e1117;}
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 14px 16px;
        border-radius: 10px;
    }
    div[data-testid="stMetricLabel"] {font-size: 0.85rem; color: #9aa4b2;}
    h1, h2, h3 {font-family: 'Segoe UI', sans-serif;}
    .stTabs [data-baseweb="tab-list"] {gap: 4px;}
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------
# DATA GENERATION (SYNTHETIC GLOBAL DATASET)
# -----------------------------------------------------------------------
@st.cache_data
def generate_data(seed: int = 42) -> pd.DataFrame:
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
                    lead_time = int(rng.integers(5, 45))
                    daily_demand_avg = round(rng.uniform(3, 120), 1)
                    demand_std = round(daily_demand_avg * rng.uniform(0.1, 0.5), 1)
                    service_level_z = rng.choice([1.28, 1.65, 1.96, 2.05], p=[0.2, 0.4, 0.3, 0.1])
                    safety_stock = round(service_level_z * demand_std * np.sqrt(lead_time), 0)
                    reorder_point = round(daily_demand_avg * lead_time + safety_stock, 0)
                    on_hand = round(max(0, rng.normal(reorder_point * rng.uniform(0.4, 1.8), reorder_point * 0.2)), 0)
                    unit_cost = round(rng.uniform(1.5, 250), 2)
                    moq = int(rng.choice([50, 100, 200, 500, 1000]))
                    lot_size = int(rng.choice([100, 250, 500, 1000, 2000]))
                    open_po_qty = int(rng.choice([0, 0, 0, moq, moq * 2]))
                    days_of_supply = round(on_hand / daily_demand_avg, 1) if daily_demand_avg > 0 else 0
                    abc_score = daily_demand_avg * unit_cost

                    rows.append(
                        dict(
                            sku_id=f"SKU-{sku_id}",
                            region=region,
                            country=country,
                            category=category,
                            item=item,
                            supplier=rng.choice(suppliers),
                            lead_time_days=lead_time,
                            daily_demand_avg=daily_demand_avg,
                            demand_std=demand_std,
                            service_level_z=service_level_z,
                            safety_stock=safety_stock,
                            reorder_point=reorder_point,
                            on_hand_qty=on_hand,
                            unit_cost=unit_cost,
                            moq=moq,
                            lot_size=lot_size,
                            open_po_qty=open_po_qty,
                            days_of_supply=days_of_supply,
                            abc_value=abc_score,
                        )
                    )

    df = pd.DataFrame(rows)

    # Replenishment logic
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

    # ABC classification (by cumulative value contribution)
    df = df.sort_values("abc_value", ascending=False).reset_index(drop=True)
    df["cum_pct"] = df["abc_value"].cumsum() / df["abc_value"].sum()
    df["abc_class"] = np.select(
        [df["cum_pct"] <= 0.8, df["cum_pct"] <= 0.95],
        ["A", "B"],
        default="C",
    )

    return df


df = generate_data()

# -----------------------------------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------------------------------
st.sidebar.title("📦 Filter Data")
st.sidebar.caption("Global Inventory & Replenishment Dashboard")

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
st.sidebar.caption("Data: synthetic demo dataset, generated on the fly.")

# -----------------------------------------------------------------------
# HEADER + KPI
# -----------------------------------------------------------------------
st.title("📦 Global Inventory & Replenishment Dashboard")
st.caption("Ringkasan kesehatan inventory, sinyal replenishment, dan prioritas aksi lintas region & kategori.")

total_value = filtered["inventory_value"].sum()
total_skus = filtered["sku_id"].nunique()
below_rop_count = filtered["below_rop"].sum()
critical_count = (filtered["stockout_risk"] == "Critical").sum()
avg_dos = filtered["days_of_supply"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Inventory Value", f"${total_value:,.0f}")
c2.metric("Total SKU Aktif", f"{total_skus:,}")
c3.metric("SKU di Bawah ROP", f"{below_rop_count:,}", delta=f"{below_rop_count/total_skus*100:.1f}% dari total" if total_skus else "0")
c4.metric("SKU Risiko Critical", f"{critical_count:,}")
c5.metric("Rata-rata Days of Supply", f"{avg_dos:.1f} hari")

st.markdown("---")

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
            color="inventory_value",
            color_continuous_scale="Blues",
        )
        fig_region.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig_region, use_container_width=True)

    with colB:
        risk_summary = filtered["stockout_risk"].value_counts().reindex(["Critical", "High", "Medium", "Low"]).fillna(0)
        fig_risk = px.pie(
            names=risk_summary.index,
            values=risk_summary.values,
            title="Distribusi Stockout Risk",
            color=risk_summary.index,
            color_discrete_map={"Critical": "#e74c3c", "High": "#e67e22", "Medium": "#f1c40f", "Low": "#2ecc71"},
            hole=0.45,
        )
        fig_risk.update_layout(height=380)
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
            color_continuous_scale="Teal",
        )
        fig_tree.update_layout(height=420)
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
            color_continuous_scale="RdYlGn",
        )
        fig_dos.update_layout(height=420, coloraxis_showscale=False)
        st.plotly_chart(fig_dos, use_container_width=True)

# --- TAB 2: REPLENISHMENT PRIORITY ---
with tab2:
    st.subheader("🚨 SKU yang Butuh Tindakan Replenishment")
    action_df = filtered[filtered["below_rop"]].copy()
    action_df = action_df.sort_values(["stockout_risk", "abc_class", "days_of_supply"])

    st.write(
        f"**{len(action_df):,} SKU** saat ini berada di bawah Reorder Point (ROP) dan memerlukan order."
    )

    display_cols = [
        "sku_id", "item", "region", "country", "category", "supplier",
        "on_hand_qty", "open_po_qty", "reorder_point", "days_of_supply",
        "stockout_risk", "abc_class", "suggested_order_qty", "unit_cost",
    ]
    st.dataframe(
        action_df[display_cols].style.format(
            {
                "on_hand_qty": "{:,.0f}",
                "open_po_qty": "{:,.0f}",
                "reorder_point": "{:,.0f}",
                "days_of_supply": "{:.1f}",
                "suggested_order_qty": "{:,.0f}",
                "unit_cost": "${:.2f}",
            }
        ),
        use_container_width=True,
        height=420,
    )

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
            color_discrete_map={"Critical": "#e74c3c", "High": "#e67e22", "Medium": "#f1c40f", "Low": "#2ecc71"},
            title="Top 10 Estimasi Nilai Order Replenishment",
        )
        fig_order.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
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
            color="suggested_order_qty",
            color_continuous_scale="Purples",
        )
        fig_supplier.update_layout(height=420, coloraxis_showscale=False)
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
            color_discrete_map={"A": "#2ecc71", "B": "#f1c40f", "C": "#e74c3c"},
            title="Inventory Value per ABC Class",
        )
        fig_abc.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_abc, use_container_width=True)

    with colH:
        fig_scatter = px.scatter(
            filtered,
            x="daily_demand_avg",
            y="lead_time_days",
            size="inventory_value",
            color="abc_class",
            hover_name="item",
            color_discrete_map={"A": "#2ecc71", "B": "#f1c40f", "C": "#e74c3c"},
            title="Demand vs Lead Time (bubble = inventory value)",
        )
        fig_scatter.update_layout(height=400)
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
    st.subheader("Ringkasan per Kategori")
    st.dataframe(
        cat_summary.style.format(
            {"inventory_value": "${:,.0f}", "avg_dos": "{:.1f}"}
        ),
        use_container_width=True,
    )

# --- TAB 4: RAW DATA ---
with tab4:
    st.subheader("📋 Detail Seluruh SKU (sesuai filter)")
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=550)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download data (CSV)", csv, "inventory_replenishment_data.csv", "text/csv")

st.markdown("---")
st.caption(
    "Dashboard demo — data bersifat sintetis untuk keperluan ilustrasi analisis SCM/Inventory Management. "
    "Metodologi: ROP = (rata-rata demand harian × lead time) + safety stock; "
    "Safety stock = Z × σ_demand × √(lead time); ABC class berdasarkan kontribusi kumulatif nilai konsumsi."
)

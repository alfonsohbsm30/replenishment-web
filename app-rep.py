import streamlit as st
import pandas as pd
from datetime import datetime

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Small CSS polish — tighter metric cards, subtle borders
st.markdown(
    """
    <style>
        div[data-testid="stMetric"] {
            background-color: rgba(240, 242, 246, 0.5);
            border: 1px solid rgba(49, 51, 63, 0.1);
            border-radius: 10px;
            padding: 12px 16px;
        }
        .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

CATEGORIES = ["Electronics", "Furniture", "Stationery", "Apparel", "Other"]

# =============================================================================
# SESSION STATE — MOCK DATABASE
# =============================================================================
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(
        [
            {"Product ID": "P1001", "Name": "Wireless Mouse", "Category": "Electronics", "Stock": 45, "Price": 25.99, "Reorder Level": 15},
            {"Product ID": "P1002", "Name": "Mechanical Keyboard", "Category": "Electronics", "Stock": 8, "Price": 89.99, "Reorder Level": 10},
            {"Product ID": "P1003", "Name": "Office Chair", "Category": "Furniture", "Stock": 14, "Price": 149.50, "Reorder Level": 5},
            {"Product ID": "P1004", "Name": "Notebook Journal", "Category": "Stationery", "Stock": 3, "Price": 4.99, "Reorder Level": 20},
        ]
    )

if "last_updated" not in st.session_state:
    st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")


def touch():
    """Record the timestamp of the last data change."""
    st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")


# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.title("📦 Navigation")
app_mode = st.sidebar.radio("Go to", ["Dashboard", "Manage Stock", "Add New Product"])
st.sidebar.markdown("---")
st.sidebar.caption(f"Last updated: {st.session_state.last_updated}")

df = st.session_state.inventory

# Guard against an empty table (e.g. after deleting every row)
if df.empty:
    total_products, total_value, low_stock_count = 0, 0.0, 0
    low_stock_items = df
else:
    total_products = len(df)
    total_value = (df["Stock"] * df["Price"]).sum()
    low_stock_items = df[df["Stock"] <= df["Reorder Level"]]
    low_stock_count = len(low_stock_items)

st.sidebar.metric("Products tracked", total_products)
st.sidebar.metric("Inventory value", f"${total_value:,.2f}")

# Export current inventory as CSV from anywhere in the app
st.sidebar.download_button(
    "⬇️ Export inventory (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"inventory_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    use_container_width=True,
)

# =============================================================================
# DASHBOARD
# =============================================================================
if app_mode == "Dashboard":
    st.title("📦 Inventory Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Unique Products", total_products)
    col2.metric("Total Inventory Value", f"${total_value:,.2f}")
    col3.metric("Low Stock Alerts ⚠️", low_stock_count)

    if low_stock_count > 0:
        st.warning(f"⚠️ **{low_stock_count} item(s)** have dropped to or below their reorder threshold.")
        with st.expander("View low stock items", expanded=True):
            st.dataframe(
                low_stock_items[["Product ID", "Name", "Stock", "Reorder Level"]],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.success("✅ All items are above their reorder threshold.")

    st.markdown("---")
    st.subheader("Current Stock")

    search_col, cat_col = st.columns([2, 1])
    with search_col:
        search_query = st.text_input("🔍 Search by product name", "")
    with cat_col:
        category_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES)

    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df["Name"].str.contains(search_query, case=False, na=False)]
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["Category"] == category_filter]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.markdown("---")
        st.subheader("Inventory value by category")
        value_by_cat = df.assign(Value=df["Stock"] * df["Price"]).groupby("Category")["Value"].sum()
        st.bar_chart(value_by_cat)

# =============================================================================
# MANAGE STOCK — INLINE EDIT & DELETE
# =============================================================================
elif app_mode == "Manage Stock":
    st.title("⚙️ Manage Stock Levels")
    st.caption("Edit any cell directly. Select a row's checkbox and press **Delete** to remove it, or use the blank bottom row to add a line quickly.")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product ID": st.column_config.TextColumn("Product ID", disabled=True, help="Locked — set when the product is created"),
            "Category": st.column_config.SelectboxColumn("Category", options=CATEGORIES),
            "Stock": st.column_config.NumberColumn("Current Stock", min_value=0, step=1),
            "Price": st.column_config.NumberColumn("Price ($)", min_value=0.0, format="$%.2f"),
            "Reorder Level": st.column_config.NumberColumn("Reorder Level", min_value=0, step=1),
        },
        key="stock_editor",
    )

    if st.button("💾 Save All Modifications", type="primary"):
        st.session_state.inventory = edited_df.reset_index(drop=True)
        touch()
        st.success("Inventory updated successfully!")
        st.rerun()

# =============================================================================
# ADD NEW PRODUCT
# =============================================================================
elif app_mode == "Add New Product":
    st.title("➕ Add New Inventory Product")

    with st.form("new_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            p_id = st.text_input("Product ID (e.g., P1005)")
            p_name = st.text_input("Product Name")
            p_cat = st.selectbox("Category", CATEGORIES)
        with col2:
            p_stock = st.number_input("Initial Stock Level", min_value=0, value=0, step=1)
            p_price = st.number_input("Unit Price ($)", min_value=0.0, value=0.0, step=0.01)
            p_reorder = st.number_input("Reorder Threshold Alert", min_value=0, value=5, step=1)

        submit_button = st.form_submit_button("Add Item to System")

        if submit_button:
            if not p_id.strip() or not p_name.strip():
                st.error("Please fill out both the Product ID and Product Name.")
            elif p_id in df["Product ID"].values:
                st.error("This Product ID already exists. Please use a unique ID.")
            else:
                new_row = {
                    "Product ID": p_id.strip(),
                    "Name": p_name.strip(),
                    "Category": p_cat,
                    "Stock": int(p_stock),
                    "Price": float(p_price),
                    "Reorder Level": int(p_reorder),
                }
                st.session_state.inventory = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                touch()
                st.success(f"Successfully added '{p_name}' to system inventory!")

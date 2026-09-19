import streamlit as tf
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide"
)

# 2. Initialize Session State for Mock Database
if "inventory" not in st.session_state:
    # Pre-populate with initial dummy data
    st.session_state.inventory = pd.DataFrame([
        {"Product ID": "P1001", "Name": "Wireless Mouse", "Category": "Electronics", "Stock": 45, "Price": 25.99, "Reorder Level": 15},
        {"Product ID": "P1002", "Name": "Mechanical Keyboard", "Category": "Electronics", "Stock": 8, "Price": 89.99, "Reorder Level": 10},
        {"Product ID": "P1003", "Name": "Office Chair", "Category": "Furniture", "Stock": 14, "Price": 149.50, "Reorder Level": 5},
        {"Product ID": "P1004", "Name": "Notebook Journal", "Category": "Stationery", "Stock": 3, "Price": 4.99, "Reorder Level": 20},
    ])

# 3. Sidebar Header & KPI Metrics
st.sidebar.title("Navigation & Controls")
app_mode = st.sidebar.radio("Go to", ["Dashboard & View", "Manage Stock", "Add New Product"])

# Calculate high-level metrics
df = st.session_state.inventory
total_products = len(df)
total_value = (df["Stock"] * df["Price"]).sum()
low_stock_items = df[df["Stock"] <= df["Reorder Level"]]
low_stock_count = len(low_stock_items)

# --- APP MODE: DASHBOARD ---
if app_mode == "Dashboard & View":
    st.title("📦 Inventory Dashboard")
    
    # Display Top Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Unique Products", total_products)
    col2.metric("Total Inventory Value", f"${total_value:,.2f}")
    col3.metric("Low Stock Alerts ⚠️", low_stock_count, delta_color="inverse")
    
    # Show Alerts if Low Stock Exists
    if low_stock_count > 0:
        st.warning(f"⚠️ **Alert:** {low_stock_count} item(s) have dropped below their minimum reorder thresholds!")
        with st.expander("View Low Stock Items"):
            st.dataframe(low_stock_items[["Product ID", "Name", "Stock", "Reorder Level"]])
            
    st.markdown("---")
    st.subheader("Current Stock Inventory")
    
    # Simple search filter
    search_query = st.text_input("🔍 Search products by name...", "")
    if search_query:
        filtered_df = df[df["Name"].str.contains(search_query, case=False)]
    else:
        filtered_df = df
        
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# --- APP MODE: MANAGE STOCK (INLINE EDIT & DELETE) ---
elif app_mode == "Manage Stock":
    st.title("⚙️ Manage Stock Levels")
    st.markdown("Modify item cells directly inside the table below. Use the **bottom row** to add lines, or select a row and hit **Delete** on your keyboard.")
    
    # Data Editor allows real-time interactive dataframe modifications
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product ID": st.column_config.TextColumn("Product ID", disabled=True), # Lock key identifier
            "Stock": st.column_config.NumberColumn("Current Stock", min_value=0, step=1),
            "Price": st.column_config.NumberColumn("Price ($)", min_value=0.0, format="$%.2f"),
        }
    )
    
    # Save button updates the global session state
    if st.button("💾 Save All Modifications", type="primary"):
        st.session_state.inventory = edited_df.reset_index(drop=True)
        st.success("Inventory updated successfully!")
        st.rerun()

# --- APP MODE: ADD NEW PRODUCT ---
elif app_mode == "Add New Product":
    st.title("➕ Add New Inventory Product")
    
    with st.form("new_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            p_id = st.text_input("Product ID (e.g., P1005)")
            p_name = st.text_input("Product Name")
            p_cat = st.selectbox("Category", ["Electronics", "Furniture", "Stationery", "Apparel", "Other"])
        with col2:
            p_stock = st.number_input("Initial Stock Level", min_value=0, value=0, step=1)
            p_price = st.number_input("Unit Price ($)", min_value=0.0, value=0.0, step=0.01)
            p_reorder = st.number_input("Reorder Threshold Alert", min_value=0, value=5, step=1)
            
        submit_button = st.form_submit_with_clicks("Add Item to System")
        
        if submit_button:
            if not p_id or not p_name:
                st.error("Please fill out both the Product ID and Product Name.")
            elif p_id in df["Product ID"].values:
                st.error("This Product ID already exists. Please use a unique ID.")
            else:
                # Append row to DataFrame
                new_row = {
                    "Product ID": p_id,
                    "Name": p_name,
                    "Category": p_cat,
                    "Stock": int(p_stock),
                    "Price": float(p_price),
                    "Reorder Level": int(p_reorder)
                }
                st.session_state.inventory = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Successfully added '{p_name}' to system inventory!")

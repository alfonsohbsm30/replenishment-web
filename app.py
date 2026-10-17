import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Inventory Management Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF5757;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #0A2540;
    }
    h2 {
        color: #0A2540;
    }
    h3 {
        color: #FF5757;
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data
def load_data(business_type):
    """Load inventory data based on business type"""
    data_files = {
        "Plant Nursery": "data/nursery_inventory.csv",
        "Retail Storefront": "data/retail_inventory.csv",
        "Service Business": "data/service_inventory.csv"
    }
    
    df = pd.read_csv(data_files[business_type])
    
    # Calculate metrics
    df['total_value'] = df['quantity_on_hand'] * df['cost_per_unit']
    df['needs_reorder'] = df['quantity_on_hand'] <= df['reorder_point']
    df['stock_status'] = df.apply(lambda row: 
        'Critical' if row['quantity_on_hand'] < row['reorder_point'] * 0.5
        else 'Low' if row['quantity_on_hand'] <= row['reorder_point']
        else 'Good', axis=1)
    
    # Calculate turnover (simplified - assuming 30 day period)
    if 'units_sold_30d' in df.columns:
        df['turnover_rate'] = (df['units_sold_30d'] / df['quantity_on_hand']).round(2)
        df['days_of_inventory'] = (df['quantity_on_hand'] / (df['units_sold_30d'] / 30)).round(1)
        df['days_of_inventory'] = df['days_of_inventory'].replace([np.inf, -np.inf], 999)
    elif 'units_used_30d' in df.columns:
        df['usage_rate'] = (df['units_used_30d'] / df['quantity_on_hand']).round(2)
        df['days_of_inventory'] = (df['quantity_on_hand'] / (df['units_used_30d'] / 30)).round(1)
        df['days_of_inventory'] = df['days_of_inventory'].replace([np.inf, -np.inf], 999)
    
    return df

def calculate_abc_analysis(df, value_col='total_value'):
    """Perform ABC analysis on inventory"""
    df_sorted = df.sort_values(value_col, ascending=False)
    df_sorted['cumulative_value'] = df_sorted[value_col].cumsum()
    total_value = df_sorted[value_col].sum()
    df_sorted['cumulative_percent'] = (df_sorted['cumulative_value'] / total_value * 100)
    
    df_sorted['abc_class'] = df_sorted['cumulative_percent'].apply(lambda x:
        'A' if x <= 70 else 'B' if x <= 90 else 'C')
    
    return df_sorted

# Main app
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## 📦 Inventory Pro")
        st.title("Dashboard Controls")
        
        business_type = st.selectbox(
            "Select Business Type",
            ["Plant Nursery", "Retail Storefront", "Service Business"],
            help="Choose the type of business to view inventory for"
        )
        
        st.markdown("---")
        st.markdown("### About This Dashboard")
        st.markdown("""
        This interactive dashboard demonstrates inventory management 
        across three different business models:
        
        - **Plant Nursery**: Manufacturing/growing plants
        - **Retail Storefront**: Traditional retail inventory
        - **Service Business**: Equipment & supplies tracking
        """)
        
        st.markdown("---")
        st.markdown("**Created by Andrew Felt**")
        st.markdown("[Portfolio](https://andrewfelt.com) | [GitHub](https://github.com)")
    
    # Load data
    df = load_data(business_type)
    
    # Header
    st.title("📦 Inventory Management Dashboard")
    st.markdown(f"### {business_type} Analytics")
    st.markdown("---")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_items = len(df)
        st.metric(
            "Total SKUs",
            f"{total_items:,}",
            help="Total number of unique items in inventory"
        )
    
    with col2:
        total_value = df['total_value'].sum()
        st.metric(
            "Total Inventory Value",
            f"${total_value:,.2f}",
            help="Total value of all inventory at cost"
        )
    
    with col3:
        reorder_needed = df['needs_reorder'].sum()
        reorder_pct = (reorder_needed / total_items * 100)
        st.metric(
            "Items Needing Reorder",
            f"{reorder_needed}",
            f"{reorder_pct:.1f}%",
            delta_color="inverse",
            help="Items at or below reorder point"
        )
    
    with col4:
        critical_items = len(df[df['stock_status'] == 'Critical'])
        st.metric(
            "Critical Stock Items",
            f"{critical_items}",
            delta=f"-{critical_items}" if critical_items > 0 else "All Good",
            delta_color="inverse",
            help="Items below 50% of reorder point"
        )
    
    st.markdown("---")
    
    # Two column layout for charts
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Stock Status Distribution")
        status_counts = df['stock_status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color=status_counts.index,
            color_discrete_map={'Good': '#10B981', 'Low': '#F39C12', 'Critical': '#FF5757'},
            hole=0.4
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        fig_status.update_layout(showlegend=True, height=350)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        st.subheader("📈 Inventory Value by Category")
        category_col = 'category' if 'category' in df.columns else df.columns[2]
        category_value = df.groupby(category_col)['total_value'].sum().sort_values(ascending=False).head(10)
        
        fig_category = px.bar(
            x=category_value.values,
            y=category_value.index,
            orientation='h',
            labels={'x': 'Total Value ($)', 'y': 'Category'},
            color=category_value.values,
            color_continuous_scale=['#0A2540', '#FF5757']
        )
        fig_category.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_category, use_container_width=True)
    
    # ABC Analysis
    st.markdown("---")
    st.subheader("💎 ABC Analysis - Pareto Principle")
    st.markdown("Items classified by value contribution: **A** (top 70%), **B** (70-90%), **C** (90-100%)")
    
    df_abc = calculate_abc_analysis(df, 'total_value')
    
    col1, col2, col3 = st.columns(3)
    
    abc_counts = df_abc['abc_class'].value_counts()
    abc_values = df_abc.groupby('abc_class')['total_value'].sum()
    
    with col1:
        a_count = abc_counts.get('A', 0)
        a_pct = (a_count / len(df) * 100)
        st.metric("Class A Items", f"{a_count}", f"{a_pct:.1f}% of SKUs")
        st.caption(f"Value: ${abc_values.get('A', 0):,.2f}")
    
    with col2:
        b_count = abc_counts.get('B', 0)
        b_pct = (b_count / len(df) * 100)
        st.metric("Class B Items", f"{b_count}", f"{b_pct:.1f}% of SKUs")
        st.caption(f"Value: ${abc_values.get('B', 0):,.2f}")
    
    with col3:
        c_count = abc_counts.get('C', 0)
        c_pct = (c_count / len(df) * 100)
        st.metric("Class C Items", f"{c_count}", f"{c_pct:.1f}% of SKUs")
        st.caption(f"Value: ${abc_values.get('C', 0):,.2f}")
    
    # Reorder Alerts
    st.markdown("---")
    st.subheader("🚨 Reorder Alerts")
    
    reorder_df = df[df['needs_reorder']].copy()
    reorder_df = reorder_df.sort_values('stock_status', 
                                        key=lambda x: x.map({'Critical': 0, 'Low': 1, 'Good': 2}))
    
    if len(reorder_df) > 0:
        display_cols = ['sku', 'product_name', 'quantity_on_hand', 'reorder_point', 
                       'stock_status', 'total_value']
        
        # Add supplier if exists
        if 'supplier' in reorder_df.columns:
            display_cols.append('supplier')
        
        st.dataframe(
            reorder_df[display_cols].style.apply(
                lambda x: ['background-color: #fee2e2' if x['stock_status'] == 'Critical'
                          else 'background-color: #fef3c7' if x['stock_status'] == 'Low'
                          else '' for _ in x.index],
                axis=1
            ),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("✅ All items are adequately stocked!")
    
    # Inventory Details with Search and Filter
    st.markdown("---")
    st.subheader("🔍 Detailed Inventory View")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("Search by SKU or Product Name", "")
    
    with col2:
        category_col = 'category' if 'category' in df.columns else df.columns[2]
        categories = ['All'] + sorted(df[category_col].unique().tolist())
        selected_category = st.selectbox("Filter by Category", categories)
    
    with col3:
        status_filter = st.selectbox("Filter by Status", ['All', 'Good', 'Low', 'Critical'])
    
    # Apply filters
    filtered_df = df.copy()
    
    if search:
        filtered_df = filtered_df[
            filtered_df['sku'].str.contains(search, case=False, na=False) |
            filtered_df['product_name'].str.contains(search, case=False, na=False)
        ]
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df[category_col] == selected_category]
    
    if status_filter != 'All':
        filtered_df = filtered_df[filtered_df['stock_status'] == status_filter]
    
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)
    
    # Download option
    st.markdown("---")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Inventory Report (CSV)",
        data=csv,
        file_name=f"{business_type.lower().replace(' ', '_')}_inventory_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()

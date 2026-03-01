"""
Streamlit Homework: Sales Dashboard
Run with: streamlit run dashboard.py

Build a complete sales dashboard with:
- Sidebar filters (date range, category, region, status)
- KPI metrics row
- Multiple chart tabs (Overview, By Category, By Region, Data)
"""
import plotly as plt
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- Page Config ---
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# --- Load Data ---
DATA_PATH = Path(__file__).parent / "data" / "sales_dashboard.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["revenue"] = df["quantity"] * df["unit_price"]
    return df


df = load_data()

st.title("📊 Sales Dashboard")

# =====================================================================
# TODO 1: Sidebar Filters
# =====================================================================
# Create a sidebar with the following filters:
st.sidebar.header("Filters")
# 1. Date range:
#    - Use st.sidebar.date_input for a start date and an end date
#    - Default to the min and max dates in the dataset
min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()
start_date = st.sidebar.date_input("Start date", value=min_date, min_value=min_date, max_value = max_date)
end_date= st.sidebar.date_input("End date", value = max_date,min_value = min_date,max_value= max_date)

#
# 2. Categories:
#    - Use st.sidebar.multiselect
#    - Options: all unique categories from the dataset
#    - Default: all selected
#
selected_cateogries = st.sidebar.multiselect("Categories", options = df['category'].unique().tolist())
# 3. Regions:
#    - Use st.sidebar.multiselect
#    - Options: all unique regions from the dataset
#    - Default: all selected
#
selected_regions = st.sidebar.multiselect("Region", options = df['region'].unique().tolist())

# 4. Status:
#    - Use st.sidebar.multiselect
#    - Options: all unique statuses from the dataset
#    - Default: all selected
selected_status = st.sidebar.multiselect("Status", options = df['status'].unique().tolist())



# Your filter code here...


# =====================================================================
# TODO 2: Apply Filters
# =====================================================================
# Filter the DataFrame using all the sidebar values from TODO 1.
# Combine conditions with & (and).
# Store the result in a variable called `filtered`.
#
# Hint: df["order_date"].dt.date converts datetime to date for comparison

filtered = df[
                (df['order_date'].dt.date>=start_date)
              & (df['order_date'].dt.date<=end_date)
              & (df['region'].isin(selected_regions))
              & (df['category'].isin(selected_cateogries))
              & (df['status'].isin(selected_status))]

st.caption(f'Showing {len(filtered)} of {len(df)} orders')  # Replace this with the filtered version


# =====================================================================
# TODO 3: KPI Metrics Row
# =====================================================================
# Create 4 columns using st.columns(4) and display these metrics:
col1,col2,col3,col4 = st.columns(4)

# Column 1: Total Revenue — sum of filtered["revenue"], formatted as $X,XXX.XX
filtered['Revenue'] = filtered['quantity'] * filtered['unit_price']
total_revenue = filtered['Revenue'].sum()
col1.metric('Total Revenue',f'${total_revenue:,.2f}')
# Column 2: Total Orders — number of rows in filtered
total_orders = len(filtered['order_id'].unique())
col2.metric('Total Orders',total_orders)
# Column 3: Average Order Value — mean of filtered["revenue"], formatted as $X,XXX.XX
try:
    average_order_value = total_revenue/total_orders
    top_category = filtered.groupby('category')['Revenue'].sum().idxmax() 
except Exception as e:
    average_order_value = 0
    top_category = 'NaN'

col3.metric('Average Order Value',f'${average_order_value:,.2f}')
# Column 4: Top Category — category with the highest total revenue
col4.metric('Top Category', top_category)

# Hint: Use col.metric("Label", "Value")
# Hint: Handle the case where filtered is empty (total_orders == 0)


# =====================================================================
# TODO 4: Visualization Tabs
# =====================================================================
# Create 4 tabs: "Overview", "By Category", "By Region", "Data"
tab1,tab2,tab3,tab4 = st.tabs(['Overview',' By Category','By Region','Data'])
# Overview tab:
#   - Monthly revenue line chart
#   - Group by month: filtered.groupby(filtered["orders_date"].dt.to_period("M"))
#   - Use px.line with markers=True

if len(filtered)>0:
    monthly = filtered.groupby(filtered['order_date'].dt.to_period('M'))['Revenue'].sum().reset_index()
    monthly['order_date'] = monthly['order_date'].astype(str)
    fig = px.line(x=monthly['order_date'],y=monthly['Revenue'],markers = True)
    tab1.plotly_chart(fig,use_container_width = True)
else:
    tab1.write('No data to be displayed')

# By Category tab:
#   - Horizontal bar chart of revenue by category
#   - Use px.bar with orientation="h"
#   - Sort by revenue ascending (so highest is at top)
if len(filtered)>0:
    category_df = filtered.groupby('category')['Revenue'].sum().reset_index()
    fig2 = px.bar(category_df,x = 'Revenue',y = 'category', orientation='h',color = 'category')
    tab2.plotly_chart(fig2,use_container_width = True)
else:
    tab2.write('No data to be displayed')
# By Region tab:
#   - Pie chart of revenue by region
#   - Use px.pie
if len(filtered)>0:
    region_df = filtered.groupby('region')['Revenue'].sum().reset_index()
    fig3 = px.pie(region_df, values= 'Revenue',names = 'region')
    tab3.plotly_chart(fig3,use_container_width = True)
else:
    tab3.write('No data to be displayed')
# Data tab:
#   - Display the filtered DataFrame with st.dataframe
#   - Add a download button using st.download_button to export as CSV
if len(filtered)>0:
    st.dataframe(filtered,use_container_width=True)
    csv_data = filtered.to_csv(index = False)
    st.download_button(
        label="Download as CSV",
        data =csv_data,
        file_name = 'filtered_sales_data.csv',
        mime = 'textx/csv'
    )
else:
    tab4.write('No data to be displayed')
# For all charts, use st.plotly_chart(fig, use_container_width=True)
# Add st.info("No data to display.") when filtered is empty

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import base64

# Set page config
st.set_page_config(layout="wide", page_title="Rewards Program Dashboard Controls")

# Function to load data
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

# Load data
df = load_data()

# Sidebar controls
st.sidebar.header("Dashboard Controls")

# Date range selector
st.sidebar.subheader("Date Range")
min_date = df['Redemption_Date'].min()
max_date = df['Redemption_Date'].max()
start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Filter data based on date range
df_filtered = df[(df['Redemption_Date'] >= str(start_date)) & (df['Redemption_Date'] <= str(end_date))]

# Brand selector
selected_brands = st.sidebar.multiselect("Select Brands", options=df['Brand'].unique(), default=df['Brand'].unique())

# User segment selector
user_segments = ['High Value', 'Medium Value', 'Low Value']
selected_segments = st.sidebar.multiselect("Select User Segments", options=user_segments, default=user_segments)

# Apply filters
df_filtered = df_filtered[df_filtered['Brand'].isin(selected_brands) & df_filtered['User_Segment'].isin(selected_segments)]

# Main content
st.title("Rewards Program Dashboard Controls")

# Display key metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Users", df_filtered['Member_Name_Surname_Per_Redemption'].nunique())
col2.metric("Total Redemptions", df_filtered['Redemptions_by_User'].sum())
col3.metric("Avg. Satisfaction", f"{df_filtered['Satisfaction_Rating_on_Reward'].mean():.2f}")
col4.metric("Total Reward Value", f"${df_filtered['Reward_Value_Amount_in_Dollars'].sum():,.0f}")

# User Engagement Distribution
st.header("User Engagement Distribution")
engagement_bins = pd.cut(df_filtered['Engagement_Score'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
engagement_dist = engagement_bins.value_counts().sort_index()
fig = px.bar(x=engagement_dist.index, y=engagement_dist.values, 
             labels={'x': 'Engagement Level', 'y': 'Number of Users'},
             color=engagement_dist.index,
             color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Reward Efficiency by Brand
st.header("Reward Efficiency by Brand")
brand_efficiency = df_filtered.groupby('Brand')['Efficiency'].mean().sort_values(ascending=False)
fig = px.bar(x=brand_efficiency.index, y=brand_efficiency.values,
             labels={'x': 'Brand', 'y': 'Efficiency (Value/$)'},
             color=brand_efficiency.index,
             color_discrete_sequence=px.colors.qualitative.Pastel)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# User Segmentation Analysis
st.header("User Segmentation Analysis")
segment_counts = df_filtered['User_Segment'].value_counts()
fig = px.pie(values=segment_counts.values, names=segment_counts.index, 
             title="User Segments Distribution",
             color_discrete_sequence=px.colors.qualitative.Bold)
fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig, use_container_width=True)

# Data Export
st.header("Export Data")
if st.button("Generate CSV"):
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="filtered_rewards_data.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

# Save current state
if st.button("Save Dashboard State"):
    state = {
        'start_date': str(start_date),
        'end_date': str(end_date),
        'selected_brands': selected_brands,
        'selected_segments': selected_segments
    }
    st.json(state)
    st.success("Dashboard state saved! You can copy this JSON to restore the state later.")

# Load saved state
st.header("Load Saved State")
saved_state = st.text_area("Paste saved JSON here:")
if st.button("Load State"):
    try:
        state = eval(saved_state)
        st.success("State loaded successfully! Refresh the page to see the changes.")
        # Here you would typically update the UI elements with the loaded state
        # For demonstration, we'll just display the loaded state
        st.write(state)
    except:
        st.error("Invalid JSON. Please check the format and try again.")
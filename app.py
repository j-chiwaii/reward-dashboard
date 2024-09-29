import streamlit as st
import pandas as pd
import numpy as np
import datetime
from PIL import Image
import base64
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="Rewards Program Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Logo section
col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
# Function to convert image to base64
def get_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Get the image in base64 format
image_base64 = get_image_as_base64('logon.jpg')

with col1:
    st.markdown(
        f"""
        <div style='display: inline-block; background-color: black; padding: 10px; border-radius: 10px;'>
            <img src='data:image/jpg;base64,{image_base64}' width='100'>
        </div>
        """,
        unsafe_allow_html=True
    )

# Reading data
df = pd.read_csv("data.csv")

# Data preprocessing
df['Engagement_Score'] = df['Redemptions_by_User'] * df['Satisfaction_Rating_on_Reward']
df['Efficiency'] = df['Reward_Value_Amount_in_Dollars'] / df['Point_Value_per_Redemption']

# User segmentation
def segment_users(row):
    if row['Redemptions_by_User'] >= 7 and row['Satisfaction_Rating_on_Reward'] >= 4:
        return 'High Value'
    elif row['Redemptions_by_User'] >= 5 or row['Satisfaction_Rating_on_Reward'] >= 3.5:
        return 'Medium Value'
    else:
        return 'Low Value'

df['User_Segment'] = df.apply(segment_users, axis=1)

# Page setup
st.markdown("""
    <style>
    .main {background-color: #f0f2f6;}
    .stPlotlyChart {background-color: white; border-radius: 5px; box-shadow: 0 2px 5px 0 rgba(0,0,0,0.16);}
    .stMetric {background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px 0 rgba(0,0,0,0.16);}
    h1, h2, h3 {color: #2c3e50;}
    .metric-value {color: #3498db; font-weight: bold;}
    .metric-label {color: #7f8c8d;}
    </style>
    """, unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
with col2:
    st.markdown("<h1 style='color:black;'>🏆 Advanced Rewards Program Analytics</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:black;'>Last updated: {datetime.datetime.now().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)

# Key Metrics
st.header("📊 Key Program Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='stMetric'><p class='metric-label'>Total Users</p><p class='metric-value'>{df['Member_Name_Surname_Per_Redemption'].nunique()}</p></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='stMetric'><p class='metric-label'>Total Redemptions</p><p class='metric-value'>{df['Redemptions_by_User'].sum()}</p></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='stMetric'><p class='metric-label'>Avg. Satisfaction</p><p class='metric-value'>{df['Satisfaction_Rating_on_Reward'].mean():.2f}</p></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='stMetric'><p class='metric-label'>Total Reward Value</p><p class='metric-value'>${df['Reward_Value_Amount_in_Dollars'].sum():,.0f}</p></div>", unsafe_allow_html=True)

# New Analysis Section
st.header("🔍 User Engagement Analysis")
col1, col2 = st.columns(2)

with col1:
    # Chart 1: User Engagement Distribution
    engagement_bins = pd.cut(df['Engagement_Score'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    engagement_dist = engagement_bins.value_counts().sort_index()
    
    fig = px.bar(x=engagement_dist.index, y=engagement_dist.values, 
                 title="User Engagement Distribution",
                 labels={'x': 'Engagement Level', 'y': 'Number of Users'},
                 color=engagement_dist.index,
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Chart 2: Reward Efficiency by Brand
    brand_efficiency = df.groupby('Brand')['Efficiency'].mean().sort_values(ascending=False)
    
    fig = px.bar(x=brand_efficiency.index, y=brand_efficiency.values,
                 title="Reward Efficiency by Brand",
                 labels={'x': 'Brand', 'y': 'Efficiency (Value/$)'},
                 color=brand_efficiency.index,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# User Segmentation Analysis
st.header("👥 User Segmentation Analysis")
col1, col2 = st.columns(2)

with col1:
    segment_counts = df['User_Segment'].value_counts()
    fig = px.pie(values=segment_counts.values, names=segment_counts.index, 
                 title="User Segments Distribution",
                 color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    segment_metrics = df.groupby('User_Segment').agg({
        'Redemptions_by_User': 'mean',
        'Satisfaction_Rating_on_Reward': 'mean',
        'Reward_Value_Amount_in_Dollars': 'mean'
    }).reset_index()
    
    fig = go.Figure(data=[
        go.Bar(name='Avg. Redemptions', x=segment_metrics['User_Segment'], y=segment_metrics['Redemptions_by_User']),
        go.Bar(name='Avg. Satisfaction', x=segment_metrics['User_Segment'], y=segment_metrics['Satisfaction_Rating_on_Reward']),
        go.Bar(name='Avg. Reward Value', x=segment_metrics['User_Segment'], y=segment_metrics['Reward_Value_Amount_in_Dollars'])
    ])
    fig.update_layout(title_text='Segment Performance Comparison', barmode='group')
    st.plotly_chart(fig, use_container_width=True)

# Reward Analysis
st.header("🎁 Reward Analysis")
col1, col2 = st.columns(2)

with col1:
    reward_popularity = df['Reward_Received'].value_counts().reset_index()
    reward_popularity.columns = ['Reward', 'Count']
    fig = px.treemap(reward_popularity, path=['Reward'], values='Count',
                     title='Reward Popularity', color='Count',
                     color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    reward_satisfaction = df.groupby('Reward_Received')['Satisfaction_Rating_on_Reward'].mean().reset_index()
    fig = px.bar(reward_satisfaction, x='Reward_Received', y='Satisfaction_Rating_on_Reward',
                 title='Average Satisfaction by Reward Type',
                 color='Satisfaction_Rating_on_Reward', color_continuous_scale='RdYlGn')
    fig.update_layout(xaxis_title='Reward Type', yaxis_title='Average Satisfaction')
    st.plotly_chart(fig, use_container_width=True)

# Brand Performance
st.header("🏢 Brand Performance")
brand_perf = df.groupby('Brand').agg({
    'Reward_Value_Amount_in_Dollars': 'sum',
    'Satisfaction_Rating_on_Reward': 'mean',
    'Redemptions_by_User': 'count'
}).reset_index()

fig = px.scatter(brand_perf, x='Reward_Value_Amount_in_Dollars', y='Satisfaction_Rating_on_Reward',
                 size='Redemptions_by_User', color='Brand', hover_name='Brand',
                 title='Brand Performance Overview')
fig.update_layout(xaxis_title='Total Reward Value ($)', yaxis_title='Average Satisfaction')
st.plotly_chart(fig, use_container_width=True)

# Correlation Analysis
st.header("🔗 Correlation Analysis")
corr_matrix = df[['Redemptions_by_User', 'Satisfaction_Rating_on_Reward', 
                  'Reward_Value_Amount_in_Dollars', 'Point_Value_per_Redemption', 
                  'Cost_Per_Redemption_in_Dollars']].corr()

fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                title="Correlation Heatmap of Key Metrics",
                color_continuous_scale='RdBu_r')
st.plotly_chart(fig, use_container_width=True)
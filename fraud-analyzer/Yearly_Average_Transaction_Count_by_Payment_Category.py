import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Dataset URL
dataset_url = 'https://raw.githubusercontent.com/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Load the dataset
df = pd.read_csv(dataset_url)

# Convert 'created_at' column to datetime format
df['created_at'] = pd.to_datetime(df['created_at'])

# Calculate the yearly average transaction count for each payment category
avg_df = df.groupby(['payment_category', df['created_at'].dt.year])['id'].count().reset_index()

# Initialize Streamlit app
# st.title('Yearly Average Transaction Count by Payment Category')
st.markdown("<h1 style='text-align: center; font-size: 30px;'>Yearly Average Transaction Count by Payment Category</h1>", unsafe_allow_html=True)
st.markdown("This analysis extends to a high-level overview of transaction patterns in Centrix by continuously monitoring live transactions.")

# Plotting the pie chart using Plotly Graph Objects
fig = go.Figure(data=[go.Pie(
    labels=avg_df['payment_category'],
    values=avg_df['id'],
    title='Yearly Average Transaction Count by Payment Category'
)])

# Display the pie chart in Streamlit app
st.plotly_chart(fig)

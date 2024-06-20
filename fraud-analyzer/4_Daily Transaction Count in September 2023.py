import streamlit as st
import pandas as pd
import plotly.express as px

# Replace 'your_csv_link_here' with the actual link to your CSV file
csv_link = 'https://raw.githubusercontent.com/dilshansr/Centrix_Data/c88fd42421393ad04b0f235d78fbb199c085e37c/SampleNewDF.csv'
df = pd.read_csv(csv_link)

# Convert 'created_at' column to datetime format if not already
df['created_at'] = pd.to_datetime(df['created_at'])

# Extract year-month and set it as a new column
df['year_month'] = df['created_at'].dt.to_period('M')

# Filter data for September 2023
september_data = df[df['year_month'] == '2023-09']

# Group by date and calculate the daily transaction count
daily_transaction_count = september_data.groupby(september_data['created_at'].dt.date).size().reset_index(name='transaction_count')

# Set up the Streamlit app
st.title('Daily Transaction Count in September 2023')

# Create a line chart using Plotly Express
fig = px.line(
    daily_transaction_count,
    x='created_at',
    y='transaction_count',
    labels={'created_at': 'Date', 'transaction_count': 'Transaction Count'},
    title='Daily Transaction Count in September 2023',
)

# Display the line chart using Streamlit
st.plotly_chart(fig)

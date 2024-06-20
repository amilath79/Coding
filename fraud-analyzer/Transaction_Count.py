import streamlit as st
import pandas as pd
import plotly.express as px

# Load data from the provided CSV link
url = 'https://raw.githubusercontent.com/xxxxxxxxxxxxxxxxxxxxxx'
df = pd.read_csv(url)

# Convert 'created_at' column to datetime format if not already
df['created_at'] = pd.to_datetime(df['created_at'])

# Extract year-month and set it as a new column
df['year_month'] = df['created_at'].dt.to_period('M').astype(str)

# Set up the Streamlit app
st.title('Monthly Transaction Count in 2023')

# Create date range filter
start_date = st.date_input("Select start date", min_value=df['created_at'].min().date(), max_value=df['created_at'].max().date(), value=df['created_at'].min().date())
end_date = st.date_input("Select end date", min_value=start_date, max_value=df['created_at'].max().date(), value=df['created_at'].max().date())

# Convert date values to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data based on the selected date range
filtered_df = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

# Group by year-month and calculate the monthly transaction count
monthly_transaction_count = filtered_df.groupby('year_month').size().reset_index(name='transaction_count')

# Plotting with Plotly Express
fig = px.bar(monthly_transaction_count, x='year_month', y='transaction_count', labels={'transaction_count': 'Transaction Count'}, title='Monthly Transaction Count in 2023')
fig.update_xaxes(tickangle=45, tickmode='array', tickvals=monthly_transaction_count['year_month'], ticktext=monthly_transaction_count['year_month'])

# Display the bar chart in Streamlit
bar_chart = st.plotly_chart(fig)

# Add interactivity: Clicking on a bar in the bar chart loads a new line chart
selected_month = st.selectbox("Select a month", monthly_transaction_count['year_month'].unique())

# Filter data for the selected month
selected_month_data = df[df['year_month'] == selected_month]

# Group by day and calculate the daily transaction count
daily_transaction_count = selected_month_data.groupby(selected_month_data['created_at'].dt.day).size().reset_index(name='transaction_count')

# Plotting the line chart for daily transaction count
line_fig = px.line(daily_transaction_count, x='created_at', y='transaction_count', labels={'transaction_count': 'Transaction Count'}, title=f'Daily Transaction Count in {selected_month}')
st.plotly_chart(line_fig)

# Add interactivity: Clicking on a point in the line chart loads a new bar chart for hourly transaction count
selected_day = st.selectbox("Select a day", daily_transaction_count['created_at'].unique())

# Filter data for the selected day
selected_day_data = selected_month_data[selected_month_data['created_at'].dt.day == selected_day]

# Group by hour and calculate the hourly transaction count
hourly_transaction_count = selected_day_data.groupby(selected_day_data['created_at'].dt.hour).size().reset_index(name='transaction_count')

# Plotting the bar chart for hourly transaction count
hourly_fig = px.bar(hourly_transaction_count, x='created_at', y='transaction_count', labels={'transaction_count': 'Transaction Count'}, title=f'Hourly Transaction Count on {selected_day}')
st.plotly_chart(hourly_fig)

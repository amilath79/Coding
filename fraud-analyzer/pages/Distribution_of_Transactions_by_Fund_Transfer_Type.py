import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import mysql.connector

# Load data from the provided CSV file
# data_url = 'https://raw.githubusercontent.com/dilshansr/Centrix_Data/c88fd42421393ad04b0f235d78fbb199c085e37c/SampleNewDF.csv'
# df = pd.read_csv(data_url)

def check_login():
    if not st.session_state.get("login_status"):
        st.warning("Please log in to access this page.")
        st.stop()  # Stop further execution if not logged in

# Connect to your MySQL database
conn = mysql.connector.connect(
host="cf-live-instance-1.cffbyc0akued.us-east-2.rds.amazonaws.com",
user="analyzerDbUser",
password="7eocmV5ZxQN0",
database="cf_live_app",
charset="utf8mb4",
port=3306)

check_login()

# Your SQL query
query = """
SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
        t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
        t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
        t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
        t1.platform, t1.status
FROM transaction t1
JOIN transaction t2 ON t1.linked_tran_id = t2.id
JOIN app_user t3 ON t3.username = t1.payer_id   
AND t1.created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) -- Up to the past 6 months
AND t1.created_at < CURDATE() - INTERVAL 1 DAY 
WHERE t1.id < t2.id
"""

# Execute the query and load the result into a DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Convert 'created_at' column to datetime format if not already
df['created_at'] = pd.to_datetime(df['created_at'])

# Title
#st.title("Distribution of Transactions by Fund Transfer Type and Status")
st.markdown("<h1 style='text-align: center; font-size: 30px;'>Distribution of Transactions by Fund Transfer Type and Status</h1>", unsafe_allow_html=True)
st.markdown("This analysis understanding the breakdown of transactions by fund transfer type provides insights into the variety of financial activities in Centrix.")

# Create date range filter
date_range = st.slider("Select date range", min_value=df['created_at'].min().date(), max_value=df['created_at'].max().date(), value=(df['created_at'].min().date(), df['created_at'].max().date()))

# Convert date values to datetime objects
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

# Filter data based on the selected date range
filtered_df = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

# Query to retrieve fund_transfer_type and count of each type for the filtered data
pie_data = filtered_df['fund_transfer_type'].value_counts().reset_index()
pie_data.columns = ['fund_transfer_type', 'transaction_count']

# Create a pie chart for fund transfer type
fig_pie = go.Figure(data=[go.Pie(labels=pie_data['fund_transfer_type'], values=pie_data['transaction_count'])])
fig_pie.update_layout(title=f'Distribution of Transactions by Fund Transfer Type ({start_date.date()} to {end_date.date()})')

# Display the pie chart for fund transfer type
st.plotly_chart(fig_pie)

# Group by 'fund_transfer_type' and 'status' and calculate the count
status_counts = filtered_df.groupby(['fund_transfer_type', 'status']).size().reset_index(name='status_count')

# Create a bar chart for status count by each fund transfer type
fig_status = go.Figure()

for fund_transfer_type in status_counts['fund_transfer_type'].unique():
    subset = status_counts[status_counts['fund_transfer_type'] == fund_transfer_type]
    fig_status.add_trace(go.Bar(x=subset['status'], y=subset['status_count'], name=fund_transfer_type))

fig_status.update_layout(barmode='group', title=f'Status Distribution by Fund Transfer Type ({start_date.date()} to {end_date.date()})')

# Display the bar chart for status count by each fund transfer type
st.plotly_chart(fig_status)

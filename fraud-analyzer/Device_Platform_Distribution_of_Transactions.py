import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

# Load the dataset
# data_url = 'https://raw.githubusercontent.com/dilshansr/Centrix_Data/927fa7e9f74d614be68c0ef2b034aa388cb46e61/SampleNewDF1.csv'
# df = pd.read_csv(data_url)

def check_login():
    if not st.session_state.get("login_status"):
        st.warning("Please log in to access this page.")
        st.stop()  # Stop further execution if not logged in

# Connect to your MySQL database
conn = mysql.connector.connect(
host="xxxxxxxxxxxxxxxxxxxxxx",
user="xxxxxxxxxxxxxxxxxxxxxx",
password="xxxxxxxxxxxxxxxxxxxxxx",
database="xxxxxxxxxxxxxxxxxxxxxx",
charset="xxxxxxxxxxxxxxxxxxxxxx",
port=3306)

check_login()

# Your SQL query
query = """
SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
        t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
        t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
        t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
        t1.platform, t1.status
FROM xxxxxxxxxxxxxxxxxxxxxx t1
JOIN xxxxxxxxxxxxxxxxxxxxxx t2 ON t1.linked_tran_id = t2.id
JOIN xxxxxxxxxxxxxxxxxxxxxx t3 ON t3.username = t1.payer_id   
AND t1.created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) -- Up to the past 6 months
AND t1.created_at < CURDATE() - INTERVAL 1 DAY 
WHERE t1.id < t2.id
"""

# Execute the query and load the result into a DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Convert 'created_at' column to datetime format
df['created_at'] = pd.to_datetime(df['created_at'])

# Create default figure for the initial state
default_figure = px.bar(
    pd.DataFrame({
        'count': df['platform'].value_counts(),
        'percentage': df['platform'].value_counts(normalize=True) * 100
    }).reset_index(),
    x='count',
    y='platform',  # Use 'platform' instead of 'index'
    orientation='h',
    text='percentage',
    labels={'platform': 'Platform', 'count': 'Transaction Count', 'percentage': 'Percentage (%)'},
    title='Platform Distribution of Transactions'
)

# Define layout of the app
# st.title("Platform Distribution of Transactions")
st.markdown("<h1 style='text-align: center; font-size: 30px;'>Device Platform Distribution of Transactions</h1>", unsafe_allow_html=True)
st.markdown("This analysis promptly spots device-specific transaction analysis. Analyze transactions conducted through various device versions. This identifies the most popular devices and trends. Moreover, it monitors the success rates of transactions across different devices and investigates any issues with failed transactions.")

# Filter DataFrame based on selected date range
date_range = st.date_input("Select Date Range", [df['created_at'].min(), df['created_at'].max()])
filtered_df = df[
    (df['created_at'] >= pd.to_datetime(date_range[0])) &
    (df['created_at'] <= pd.to_datetime(date_range[1]))
]

# Group by 'platform' and calculate the count and percentage
platform_counts = filtered_df['platform'].value_counts()
platform_percentage = filtered_df['platform'].value_counts(normalize=True) * 100

# Combine counts and percentages into a DataFrame
platform_data = pd.DataFrame({'Count': platform_counts, 'Percentage': platform_percentage})

# Reset the index to include 'platform' as a column
platform_data = platform_data.reset_index()

# Format the 'Percentage' column to display only 2 decimal places
platform_data['Percentage'] = platform_data['Percentage'].round(2)

# Create a horizontal bar chart using plotly express
fig_platform = px.bar(platform_data, x='Count', y='platform', orientation='h', text='Percentage',
                    labels={'platform': 'Platform', 'Count': 'Transaction Count', 'Percentage': 'Percentage (%)'},
                    title='Device Platform Distribution of Transactions')

# Display the platform chart
platform_chart = st.plotly_chart(fig_platform)

# Check if a platform is selected before updating the top 10 device models chart
if platform_data.empty:
    st.warning("No options to select.")
else:
    # Define callback to update the top 10 device models chart based on selected platform
    selected_platform = st.selectbox('Select a platform to view top 10 device models', platform_data['platform'])
    filtered_df_platform = df[df['platform'] == selected_platform]
    top_device_models = filtered_df_platform['device_model'].value_counts().nlargest(10)
    fig_top_devices = px.bar(x=top_device_models.index, y=top_device_models.values,
                            labels={'x': 'Device Model', 'y': 'Transaction Count'},
                            title=f'Top 10 Device Models in {selected_platform}')
    st.plotly_chart(fig_top_devices)

    # Group by 'status' and calculate the count
    status_counts = filtered_df_platform['status'].value_counts()

    # Create a bar chart for success and fail statuses
    fig_status = px.bar(status_counts, x=status_counts.index, y=status_counts.values,
                        labels={'x': 'Status', 'y': 'Transaction Count'},
                        title=f'Status Distribution in {selected_platform}')
    st.plotly_chart(fig_status)

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import requests
import mysql.connector

# # Load data from the provided CSV link
# url = 'https://raw.githubusercontent.com/dilshansr/Centrix_Data/c88fd42421393ad04b0f235d78fbb199c085e37c/SampleNewDF.csv'
# response = requests.get(url)
# data = BytesIO(response.content)
# df = pd.read_csv(data)

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


# Convert 'created_at' to datetime format
df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')  # Use errors='coerce' to handle invalid dates by converting them to NaT

# Get the top 10 payers and top 10 payees
top_payers = df['payer_bank_name'].value_counts().nlargest(10).index
top_payees = df['final_payee_bank_name'].value_counts().nlargest(10).index

# Filter the DataFrame based on the top payers and payees
filtered_df = df[df['payer_bank_name'].isin(top_payers) & df['final_payee_bank_name'].isin(top_payees)]

# Set up the Streamlit app
st.markdown("<h1 style='text-align: center; font-size: 30px;'>Top 10 Bank-to-Bank Transactions</h1>", unsafe_allow_html=True)
st.markdown("This analysis promptly identifies a quick overview of the bank to bank transactions in Centrix. This highlights the payer bank and final payer bank transactions in Centrix.")

# Date range filter
if 'created_at' in df.columns:
    min_date = df['created_at'].min()
    max_date = df['created_at'].max()
    default_date = min_date + pd.Timedelta(days=(max_date - min_date).days // 2)  # Set default to the middle of the date range
    
    start_date = pd.to_datetime(st.date_input("Start Date", min_value=min_date, max_value=max_date, value=default_date))
    end_date = pd.to_datetime(st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date))

    # Filter the DataFrame based on the selected date range
    filtered_df = filtered_df[(filtered_df['created_at'] >= start_date) & (filtered_df['created_at'] <= end_date)]
else:
    st.warning("The 'created_at' column is not present in the DataFrame.")

# Radio buttons for selecting between 'Count' and 'Amount'
selected_value = st.radio('Select Metric:', ['transaction_count', 'total_amount'])

# Group by payer_bank_name, final_payee_bank_name, and calculate count and total amount
grouped_df = filtered_df.groupby(['payer_bank_name', 'final_payee_bank_name']).agg(
    transaction_count=pd.NamedAgg(column='paying_amount', aggfunc='count'),
    total_amount=pd.NamedAgg(column='paying_amount', aggfunc='sum')
).reset_index()

# Pivot the DataFrame to create a matrix of payer banks vs. final payee banks
pivot_df = grouped_df.pivot(index='payer_bank_name', columns='final_payee_bank_name', values=selected_value).fillna(0)

# Divide the values by 1000 for 'total_amount' and format the annotations accordingly
if selected_value == 'total_amount':
    pivot_df = pivot_df / 1000

# Sort the index (Y-axis) in descending order
pivot_df = pivot_df.sort_index(ascending=False)

# Plotting a heatmap with adjusted parameters for clarity and expanded cell size
fig, ax = plt.subplots(figsize=(18, 12))  # Adjust the figsize for expanded cell size
sns.heatmap(pivot_df, cmap='YlGnBu', annot=True, fmt='.1f' if selected_value == 'total_amount' else '.0f',
            cbar_kws={'label': selected_value}, linewidths=0.5, square=True, annot_kws={'size': 8})

# Adjust font size or rotate axis labels
plt.xticks(rotation=45, ha='right', fontsize=8)
plt.yticks(rotation=0, ha='right', fontsize=8)

plt.title('Bank-to-Bank Transactions')
plt.xlabel('Final Payee Bank Name')
plt.ylabel('Payer Bank Name')

# Display the heatmap image
st.pyplot(fig)

# Close the plot
plt.close()

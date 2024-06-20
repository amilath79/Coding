import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import requests
import mysql.connector

# Load data from the provided CSV link
# url = 'https://raw.githubusercontent.com/dilshansr/Centrix_Data/9292ec52ffec7d873e8b08fc5acbb8fefb77e0e7/SampleNewDF2.csv'
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


# Format final_payee_account_number as integers
df['final_payee_account_number'] = df['final_payee_account_number'].str.replace(' ', '', regex=True)
df['final_payee_account_number'] = df['final_payee_account_number'].astype(int)

# Get the top 25 payer and payee accounts
top_payers = df['payer_account_number'].value_counts().nlargest(20).index
top_payees = df['final_payee_account_number'].value_counts().nlargest(20).index

# Set up the Streamlit app
# st.title("Top 10 Payer to Payee Account Transactions")
st.markdown("<h1 style='text-align: center; font-size: 30px;'>Top 10 Payer to Payee Account Transactions</h1>", unsafe_allow_html=True)
st.markdown("This analysis promptly identifies a quick overview of the top 10 payer to payee account transactions  in Centrix.")

# Radio buttons for selecting between 'Transaction Count' and 'Total Amount'
selected_value = st.radio('Select Metric:', ['transaction_count', 'total_amount'], index=0)

# Filter the DataFrame based on the top 25 payer and payee accounts
filtered_df = df[
    (df['payer_account_number'].isin(top_payers)) &
    (df['final_payee_account_number'].isin(top_payees))
]

# Group by payer_account_number and final_payee_account_number, then calculate the selected value
if selected_value == 'transaction_count':
    heatmap_data = filtered_df.groupby(['payer_account_number', 'final_payee_account_number']).size().reset_index(name='transaction_count')
elif selected_value == 'total_amount':
    heatmap_data = filtered_df.groupby(['payer_account_number', 'final_payee_account_number'])['paying_amount'].sum().reset_index(name='total_amount')

# Pivot the DataFrame to create a matrix of payer accounts vs. payee accounts
heatmap_matrix = heatmap_data.pivot(
    index='payer_account_number',
    columns='final_payee_account_number',
    values=selected_value
).fillna(0)

# Plotting a heatmap with adjusted parameters for clarity and expanded cell size
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(heatmap_matrix, cmap='YlGnBu', annot=True, fmt='g', linewidths=0.5, square=True)

# Adjust font size or rotate axis labels if necessary
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0, ha='right')

plt.title('Top 10 Payer to Payee Account Transactions')
plt.xlabel('Payee Account Number')
plt.ylabel('Payer Account Number')

# Display the heatmap image
st.pyplot(fig)

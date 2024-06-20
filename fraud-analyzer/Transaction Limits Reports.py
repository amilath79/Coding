import streamlit as st
import pandas as pd
import mysql.connector
from db_config import DB_CONFIG
from datetime import timedelta
import mysql.connector

# Function to check login status
def check_login():
    if not st.session_state.get("login_status"):
        st.warning("Please log in to access this page.")
        st.stop()  # Stop further execution if not logged in



def load_data_from_mysql():
    connection = mysql.connector.connect(**DB_CONFIG)
    
    # Query to retrieve data from the 'your_table_name' table
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
    AND t1.created_at < CURDATE() 
    WHERE t1.id < t2.id
"""

    df = pd.read_sql(query, connection)
    connection.close()
    return df

def check_daily_limit(df, daily_limits):
    # Merge the daily limits based on 'fund_transfer_type'
    df = df.merge(pd.DataFrame(list(daily_limits.items()), columns=['fund_transfer_type', 'daily_limit']), on='fund_transfer_type')

    # Group by user, fund_transfer_type, and calculate the sum of 'paying_amount' for each group
    user_totals = df.groupby(['nic', 'fund_transfer_type', 'daily_limit']).agg(
        name=('name', 'first'),
        payer_email=('payer_email', 'first'),
        paying_amount=('paying_amount', 'sum')
    ).reset_index()

    # Filter users exceeding the daily limit
    users_exceeding_limit = user_totals[user_totals['paying_amount'] > user_totals['daily_limit']]

    # Display the users exceeding the daily limit
    st.subheader("Users exceeding daily limit by fund_transfer_type:")
    st.write(users_exceeding_limit[['nic', 'name', 'payer_email', 'fund_transfer_type', 'paying_amount', 'daily_limit']])

def check_overall_limit(df, overall_daily_limit):
    # Calculate overall daily limit for each user (identified by NIC)
    overall_sums = df.groupby('nic').agg(
        name=('name', 'first'),
        payer_email=('payer_email', 'first'),
        paying_amount=('paying_amount', 'sum')
    ).reset_index()

    overall_sums['overall_daily_limit'] = overall_daily_limit

    # Filter users exceeding overall daily limit
    users_exceeding_limit = overall_sums[overall_sums['paying_amount'] > overall_sums['overall_daily_limit']]

    # Display the users exceeding overall daily limit with additional columns
    st.subheader("Users exceeding overall daily limit:")
    st.write(users_exceeding_limit[['nic', 'name', 'payer_email', 'paying_amount', 'overall_daily_limit']])

def main():
    check_login()
    # Load data from MySQL instead of CSV
    df = load_data_from_mysql()

    # Convert the 'created_at' column to datetime format
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Define the daily limits
    daily_limits = {
        'CF_TO_CF': 250000,
        'CF_TO_OTHER': 100000,
        'OTHER_TO_OTHER': 200000,
        'OTHER_TO_CF': 250000
    }

    # Define the overall daily limit
    overall_daily_limit = 500000

    # Display title
    st.title("Transaction Limits Reports")

    # Add date range filter
    date_range = st.date_input("Select Date Range", [df['created_at'].min().date(), df['created_at'].max().date()])
    date_range = [pd.to_datetime(date) for date in date_range]  # Convert to datetime objects
    df_filtered = df[(df['created_at'] >= date_range[0]) & (df['created_at'] <= date_range[1])]

    # Check users exceeding daily limit by fund_transfer_type
    check_daily_limit(df_filtered, daily_limits)

    # Check users exceeding overall daily limit
    check_overall_limit(df_filtered, overall_daily_limit)



if __name__ == "__main__":
    main()

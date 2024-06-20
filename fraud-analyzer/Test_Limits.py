import streamlit as st
import pandas as pd

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
    # Load the data from the provided URL
    url = "https://raw.githubusercontent.com/dilshansr/Centrix_Data/main/2023-09-01_Trans.csv"
    df = pd.read_csv(url)

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
    st.title("Transaction Limits Checker")

    # Check users exceeding daily limit by fund_transfer_type
    check_daily_limit(df, daily_limits)

    # Check users exceeding overall daily limit
    check_overall_limit(df, overall_daily_limit)

if __name__ == "__main__":
    main()

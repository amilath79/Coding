import pandas as pd
import streamlit as st

def load_data(url):
    data = pd.read_csv(url, sep=',', encoding='utf-8')
    return data

def detect_anomalies(df, new_df):
    anomalies = []

    for index, row in new_df.iterrows():
        user_data = df[(df['Payer Email'] == row['Payer Email'])][['Date', 'Total', 'Source Account']]
        
        # Check if there are at least two data points
        if len(user_data) >= 2:
            # Check if 'Source Account' column exists in user_data
            previous_source_accounts = user_data['Source Account'].unique() if 'Source Account' in user_data else []

            # Check if 'New Source Account' is different from any 'Previous Source Account'
            if row['Source Account'] not in previous_source_accounts:
                anomalies.append({
                    'Transaction ID': row['Transaction ID'],
                    'Payer Email': row['Payer Email'],
                    'Payer Mobile': row['Payer Mobile'],
                    'Date': row['Date'],
                    'Time': row['Time'],
                    'Total': row['Total'],
                    'Payment Status': row['Payment Status'],
                    'Payment Method': row['Payment Method'],
                    'Payment Category': row['Payment Category'],
                    'Previous Source Accounts': previous_source_accounts.tolist(),
                    'New Source Account': row['Source Account'],
                    'Destination Account': row['Destination Account'],
                    'User Transaction History': user_data.to_dict('records'),
                    'Conclusion': "This transaction is considered an anomaly because it deviates from the user's normal transaction pattern."
                })

    return anomalies

def main():
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Bill Transaction Account Anomaly Detector</h1>", unsafe_allow_html=True)
    st.markdown("Analysis promptly spots outlier bill transactions Accounts by continuously monitoring live transactions. Simultaneously, it raises alerts, highlighting potential anomalies for immediate attention.")

    csv_url = 'https://raw.githubusercontent.com/damika9996/Word-Cloud/295bdd390d616a0df760174af426491bbba5d862/Bill_transactions.csv'
    new_csv_url = 'https://raw.githubusercontent.com/damika9996/Word-Cloud/main/FinalBill_transactions.csv'

    df = load_data(csv_url)
    new_df = load_data(new_csv_url)

    anomalies = detect_anomalies(df, new_df)

    # Display each anomaly in a modal
    for anomaly in anomalies:
        with st.expander(f"Anomaly Detected - Transaction ID: {anomaly['Transaction ID']}"):
            st.text(f'''Payer Email: {anomaly['Payer Email']}
Payer Mobile: {anomaly['Payer Mobile']}
Date: {anomaly['Date']}
Time: {anomaly['Time']}
Total: {anomaly['Total']}
Payment Status: {anomaly['Payment Status']}
Payment Method: {anomaly['Payment Method']}
Payment Category: {anomaly['Payment Category']}
Previous Source Accounts: {anomaly['Previous Source Accounts']}
New Source Account: {anomaly['New Source Account']}
Destination Account: {anomaly['Destination Account']}''')

            # Show transaction history as a table with formatted 'Total'
            st.markdown("<h2 style='text-align: Left; font-size: 20px;'>User Transaction History:</h2>", unsafe_allow_html=True)
            user_transaction_df = pd.DataFrame(anomaly['User Transaction History'])
            user_transaction_df['Total'] = user_transaction_df['Total'].map('{:,.2f}'.format)  # Format 'Total' column
            st.table(user_transaction_df)

            # Show conclusion
            st.markdown("<h2 style='text-align: Left; font-size: 20px;'>Conclusion : </h2>", unsafe_allow_html=True)
            st.write(anomaly['Conclusion'])
            st.write("\n")

if __name__ == '__main__':
    main()

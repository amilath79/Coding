import pandas as pd
import streamlit as st
from sklearn.ensemble import IsolationForest
import mysql.connector

def load_data_from_mysql(query):
    connection = mysql.connector.connect(
    host="xxxxxxxxxxxxxxxxxxxxxx",
    user="xxxxxxxxxxxxxxxxxxxxxx",
    password="xxxxxxxxxxxxxxxxxxxxxx",
    database="xxxxxxxxxxxxxxxxxxxxxx",
    charset="xxxxxxxxxxxxxxxxxxxxxx",
    port=3306)

    df = pd.read_sql(query, connection)
    df['created_at'] = pd.to_datetime(df['created_at'])
    connection.close()

    return df


def detect_anomalies(df, new_df, z_score_threshold):
    anomalies = []

    column_mapping = {
        'created_at': 'Transaction Date',
        'paying_amount': 'Amount',
        'payer_bank_name': 'Payer Bank',
        'final_payee_bank_name': 'Payee Bank'
    }

    for index, row in new_df.iterrows():
        user_data = df[df['name'] == row['name']][['created_at', 'paying_amount', 'payer_bank_name', 'final_payee_bank_name']]
        user_data = user_data.rename(columns=column_mapping)

        if len(user_data) >= 2:
            user_std = user_data['Amount'].std()

            if user_std != 0:
                z_score = (row['paying_amount'] - user_data['Amount'].mean()) / user_std

                combined_score = z_score + row['isolation_forest_score']

                if combined_score > z_score_threshold:
                    anomalies.append({
                        'ID': row['id'],
                        'Name': row['name'],
                        'NIC': row['nic'],
                        'Paying Amount': row['paying_amount'],
                        'Created At': row['created_at'],
                        'Mobile No': row['payer_mobile'],
                        'User Transaction History': user_data,
                        'Conclusion': "This transaction is considered an anomaly because it deviates from the user's normal transaction pattern."
                    })

    return anomalies

def display_anomalies(anomalies):
    for anomaly in anomalies:
        with st.expander(f"Anomaly Transaction Detected - ID: {anomaly['ID']}"):
            st.text(f'''Name: {anomaly['Name']}
NIC: {anomaly['NIC']}
Paying Amount: {anomaly['Paying Amount']}
Created At: {anomaly['Created At']}
Mobile No: {anomaly['Mobile No']} ''')

            st.markdown("<h2 style='text-align: Left; font-size: 20px;'>User Transaction History:</h2>", unsafe_allow_html=True)
            st.write(anomaly['User Transaction History'])

            st.markdown("<h2 style='text-align: Left; font-size: 20px;'>Conclusion : </h2>", unsafe_allow_html=True)
            st.write(anomaly['Conclusion'])
            st.write("\n")

def main():
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Transaction Amount Anomaly Detector</h1>", unsafe_allow_html=True)
    st.markdown("This analysis promptly spots outlier transactions in Centrix by continuously monitoring live transactions. Simultaneously, it raises alerts, highlighting potential anomalies for immediate attention.")

    
    # live query to retrieve data
    live_query = '''
        SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
        t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
        t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
        t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
        t1.platform, t1.status
        FROM xxxxxxxxxxxxxxxxxxxxxx t1
        JOIN xxxxxxxxxxxxxxxxxxxxxx t2 ON t1.linked_tran_id = t2.id
        JOIN xxxxxxxxxxxxxxxxxxxxxx t3 ON t3.username = t1.payer_id   
        AND t1.created_at >= CONCAT(CURDATE(), ' 00:00:00');
        WHERE t1.id < t2.id
    '''

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

    # Load data from MySQL
    df = load_data_from_mysql(query)
    new_df = load_data_from_mysql(live_query)

    # Add a slider for adjusting Z-score threshold
    z_score_threshold = st.slider("Z-score Threshold", min_value=5.0, max_value=10.0, value=8.0, step=1.0)

    # Train Anomaly Model
    df = train_anomaly_model(df)
    new_df = train_anomaly_model(new_df)

    anomalies = detect_anomalies(df, new_df, z_score_threshold)

    # Display anomalies
    display_anomalies(anomalies)

if __name__ == '__main__':
    main()

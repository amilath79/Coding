import pandas as pd
import streamlit as st
from sklearn.ensemble import IsolationForest

def load_data(csv_url):
    df = pd.read_csv(csv_url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def detect_anomalies(df, new_df, z_score_threshold):
    isolation_forest = IsolationForest(contamination=0.05)
    df['isolation_forest_score'] = isolation_forest.fit_predict(df[['Total']])
    new_df['isolation_forest_score'] = isolation_forest.fit_predict(new_df[['Total']])

    anomalies = []

    for index, row in new_df.iterrows():
        user_data = df[df['Payer Email'] == row['Payer Email']][['Date', 'Total']]
        
        # Check if there are at least two data points to calculate standard deviation
        if len(user_data) >= 2:
            user_std = user_data['Total'].std()

            # Check if standard deviation is not zero before calculating Z-score
            if user_std != 0:
                z_score = (row['Total'] - user_data['Total'].mean()) / user_std

                combined_score = z_score + row['isolation_forest_score']

                if combined_score > z_score_threshold:
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
                        'Source Account': row['Source Account'],
                        'Destination Account': row['Destination Account'],
                        'User Transaction History': user_data,
                        'Conclusion': "This transaction is considered an anomaly because it deviates from the user's normal transaction pattern."
                    })

    return anomalies

def main():
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Bill Transaction Amount Anomaly Detector</h1>", unsafe_allow_html=True)
    st.markdown("This analysis promptly spots outlier bill transaction amounts by continuously monitoring live transactions. Simultaneously, it raises alerts, highlighting potential anomalies for immediate attention.")

    csv_url = 'https://raw.githubusercontent.com/damika9996/Word-Cloud/295bdd390d616a0df760174af426491bbba5d862/Bill_transactions.csv'
    new_csv_url = 'https://raw.githubusercontent.com/damika9996/Word-Cloud/295bdd390d616a0df760174af426491bbba5d862/Bill_transactions.csv'

    df = load_data(csv_url)
    new_df = load_data(new_csv_url)

    # Add a slider for adjusting Z-score threshold
    z_score_threshold = st.slider("Z-score Threshold", min_value=5.0, max_value=10.0, value=5.0, step=1.0)

    anomalies = detect_anomalies(df, new_df, z_score_threshold)

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
Source Account: {anomaly['Source Account']}
Destination Account: {anomaly['Destination Account']}''')

            # Show transaction history and conclusion
            st.markdown("<h2 style='text-align: Left; font-size: 20px;'>User Transaction History:</h2>", unsafe_allow_html=True)
            st.write(anomaly['User Transaction History'])

            st.markdown("<h2 style='text-align: Left; font-size: 20px;'>Conclusion : </h2>", unsafe_allow_html=True)
            st.write(anomaly['Conclusion'])
            st.write("\n")

if __name__ == '__main__':
    main()

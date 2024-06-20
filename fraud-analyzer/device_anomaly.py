import pandas as pd
import mysql.connector
from db_config import DB_CONFIG_LOCALHOST  # Import the database configuration

# Function to load data
def load_data_from_mysql(query):
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    data = pd.read_sql(query, connection)
    connection.close()
    return data

# Function to preprocess data
def preprocess_data(prev_df, new_df):
    prev_df['created_at'] = pd.to_datetime(prev_df['created_at'])
    new_df['created_at'] = pd.to_datetime(new_df['created_at'])
    return prev_df, new_df

# Function to detect anomalies
def detect_anomalies(prev_df, new_df):
    anomalies = []

    for _, user_row in new_df[['name', 'nic']].drop_duplicates().iterrows():
        user_name = user_row['name']
        user_nic = user_row['nic']
        new_user_data = new_df[(new_df['name'] == user_name) & (new_df['nic'] == user_nic)].copy()
        prev_user_data = prev_df[(prev_df['name'] == user_name) & (prev_df['nic'] == user_nic)].copy()

        if not new_user_data.empty and not prev_user_data.empty:
            # Identify transactions in the new dataset that are not present in the previous dataset based on 'final_payee_bank_name' and 'payer_bank_name'
            new_transactions = pd.merge(new_user_data[['payer_mobile', 'created_at', 'final_payee_bank_name', 'payer_bank_name', 'paying_amount']],
                                        prev_user_data[['final_payee_bank_name', 'payer_bank_name']],
                                        indicator=True, how='left').query('_merge == "left_only"').drop('_merge', axis=1)

            if not new_transactions.empty:
                for _, transaction in new_transactions.iterrows():
                    anomalies.append((user_name, user_nic, transaction))

    return anomalies

if __name__ == "__main__":
    try:
        historical_query = """
            SELECT * FROM fa_transaction
            WHERE created_at < CURDATE() - INTERVAL 1 DAY
        """
        live_query = '''
            SELECT * FROM fa_transaction  
            WHERE created_at >= CONCAT(CURDATE(), ' 00:00:00');
        '''
        prev_df = load_data_from_mysql(historical_query)
        new_df = load_data_from_mysql(live_query)
        prev_df, new_df = preprocess_data(prev_df, new_df)
        anomalies = detect_anomalies(prev_df, new_df)
        print("Detected anomalies:")
        for anomaly in anomalies:
            user_name, user_nic, latest_transaction = anomaly
            print(f"Newly added accounts with unusual transaction patterns for {user_name} ({user_nic}):")
            print(latest_transaction)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

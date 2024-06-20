import pandas as pd
import mysql.connector
import random
from db_config import DB_CONFIG_LOCALHOST

def load_data_from_mysql(query):
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def insert_data_to_table(anomaly_id, user_name, user_nic, created_at, myjson):
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    cursor = connection.cursor()
    insert_query = "INSERT INTO bank_acc_anomaly (anomalyID, name, nic, date, myjson) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (anomaly_id, user_name, user_nic, created_at, myjson))
    connection.commit()
    cursor.close()
    connection.close()

# Function to generate unique 7-digit anomaly IDs
def generate_anomaly_id():
    return ''.join(random.choices('0123456789', k=7))

# Define SQL queries for historical and live data
historical_query = """
    SELECT * FROM fa_transaction
    WHERE created_at >= CURDATE() - INTERVAL 3 DAY AND created_at < CURDATE() - INTERVAL 1 DAY
"""

live_query = '''
    SELECT * FROM fa_transaction  
    WHERE created_at >= CURDATE() - INTERVAL 1 DAY;
'''

# Load data from SQL queries
prev_df = pd.DataFrame(load_data_from_mysql(historical_query))
new_df = pd.DataFrame(load_data_from_mysql(live_query))

# Convert timestamp columns to Arrow-compatible format
timestamp_columns = ['created_at']  # Add more timestamp columns if needed
for col in timestamp_columns:
    new_df[col] = pd.to_datetime(new_df[col])

# Convert numeric columns to appropriate numeric types
numeric_columns = ['numeric_column']  # Add more numeric columns if needed
for col in numeric_columns:
    # Check if the column exists before conversion
    if col in new_df.columns:
        new_df[col] = pd.to_numeric(new_df[col], errors='coerce')

# Identify unique users based on 'name' and 'nic'
unique_users_new = new_df[['name', 'nic']].drop_duplicates()
unique_users_prev = prev_df[['name', 'nic']].drop_duplicates()

# Merge to get a unique set of users across both datasets
unique_users = pd.concat([unique_users_new, unique_users_prev]).drop_duplicates()

for _, user_row in unique_users.iterrows():
    
    # Specify the user's name and NIC
    user_name = user_row['name']
    user_nic = user_row['nic']

    # Filter data for the specific user in both datasets
    new_user_data = new_df[(new_df['name'] == user_name) & (new_df['nic'] == user_nic)].copy()
    prev_user_data = prev_df[(prev_df['name'] == user_name) & (prev_df['nic'] == user_nic)].copy()

    # Check if there are rows in both filtered DataFrames before proceeding
    if not new_user_data.empty and not prev_user_data.empty:
        # Identify transactions in the new dataset that are not present in the previous dataset based on 'final_payee_bank_name' and 'payer_bank_name'
        new_transactions = pd.merge(new_user_data[['created_at', 'payer_mobile', 'final_payee_bank_name', 'payer_bank_name', 'paying_amount']],
                                    prev_user_data[['final_payee_bank_name', 'payer_bank_name']],
                                    indicator=True, how='left').query('_merge == "left_only"').drop('_merge', axis=1)

        # Filter transactions with 'paying_amount' > 50000
        new_transactions = new_transactions[new_transactions['paying_amount'] > 50000]

        # Display information about the latest new transaction for the current user
        if not new_transactions.empty:
            print(f"Newly added accounts with unusual transaction patterns for {user_name} ({user_nic}):")

            # Sort the new_transactions DataFrame based on 'created_at'
            new_transactions = new_transactions.sort_values(by='created_at', ascending=False)

            # Display information about the latest transaction
            latest_transaction = new_transactions.iloc[0]

            # Get the columns that exist in the DataFrame
            existing_columns = latest_transaction.index.tolist()

            # Specify the columns to include in the JSON
            columns_to_include = ['payer_mobile', 'final_payee_bank_name', 'payer_bank_name', 'paying_amount']

            # Filter columns that exist in the DataFrame
            valid_columns = [col for col in columns_to_include if col in existing_columns]

            # Create a JSON object from selected columns
            myjson = latest_transaction[valid_columns].to_json()

            # Get the created_at date
            created_at = latest_transaction['created_at']

            # Generate anomaly ID
            anomaly_id = generate_anomaly_id()

            # Insert data into the bank_acc_anomaly table
            insert_data_to_table(anomaly_id, user_name, user_nic, created_at, myjson)

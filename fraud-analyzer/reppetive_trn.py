import pandas as pd
from datetime import datetime, timedelta
import mysql.connector
from db_config import DB_CONFIG_LOCALHOST

# Function to remove '.0' from destination account numbers and commas from payer account numbers
def remove_special_chars(df):
    df['final_payee_account_number'] = df['final_payee_account_number'].astype(str).str.replace(r'\.0', '', regex=True)
    df['payer_account_number'] = df['payer_account_number'].astype(str).str.replace(',', '', regex=False)
    return df

# Function to load and process data from MySQL database
def load_data_from_mysql(query, time_window_minutes=5):
    # MySQL database connection details
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)

    # Execute the query and fetch data into a DataFrame
    df = pd.read_sql(query, connection)

    # Close the database connection
    connection.close()

    # Convert the 'created_at' column to datetime format
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Remove special characters from destination account numbers and payer account numbers
    df = remove_special_chars(df)

    # Set the time window to 5 minutes
    time_window = timedelta(minutes=time_window_minutes)

    return df, time_window

# Function to detect users with transactions meeting the specified criteria
def detect_repetitive_transactions(df, time_window):
    repetitive_transactions_dict = {}

    for _, row in df.iterrows():
        current_time = row['created_at']
        payer_account = row['payer_account_number']
        destination_account = row['final_payee_account_number']
        amount = row['paying_amount']

        # Transactions to the same destination account with the same amount within the specified time window
        same_transactions = df[
            (df['final_payee_account_number'] == destination_account) &
            (df['paying_amount'] == amount) &
            (df['created_at'] >= current_time - time_window) &
            (df['created_at'] <= current_time)
        ]

        if len(same_transactions[same_transactions['payer_account_number'] == payer_account]) >= 3:
            if payer_account not in repetitive_transactions_dict:
                repetitive_transactions_dict[payer_account] = {
                    'name': row['name'],
                    'nic': row['nic'],
                    'amount': amount,
                    'transaction_count': len(same_transactions),
                    'transactions': same_transactions[['payer_account_number', 'final_payee_account_number', 'created_at', 'status']].to_json(orient='records')
                }
            else:
                # Update count if the current count is higher
                if len(same_transactions) > repetitive_transactions_dict[payer_account]['transaction_count']:
                    repetitive_transactions_dict[payer_account]['transaction_count'] = len(same_transactions)
                    repetitive_transactions_dict[payer_account]['transactions'] = same_transactions[['payer_account_number', 'final_payee_account_number', 'created_at', 'status']].to_json(orient='records')

    return list(repetitive_transactions_dict.values())


# Main function to load data, detect repetitive transactions, and insert into the database
# Main function to load data, detect repetitive transactions, and insert into the database
def main():
    query = '''
    SELECT * FROM fa_transaction  
        WHERE created_at >= CONCAT(CURDATE(), ' 00:00:00');
    '''
    data, time_window = load_data_from_mysql(query)
    repetitive_transactions = detect_repetitive_transactions(data, time_window)

    # MySQL database connection details
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    cursor = connection.cursor()

    # Check if each repetitive transaction already exists in the database
    for info in repetitive_transactions:
        name = info['name']
        nic = info['nic']
        amount = info['amount']
        transactions_json = info['transactions']

        # Query to check if the record already exists
        check_query = "SELECT COUNT(*) FROM repettive_trans WHERE name = %s AND nic = %s AND json = %s AND amount = %s"
        cursor.execute(check_query, (name, nic, transactions_json, amount))
        result = cursor.fetchone()


        # If record does not exist, insert it into the database
        if result[0] == 0:
            count = info['transaction_count']
            insert_query = "INSERT INTO repettive_trans (name, nic, count, json, amount) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (name, nic, count, transactions_json, amount))

    # Commit the transaction and close the connection
    connection.commit()
    connection.close()


if __name__ == '__main__':
    main()

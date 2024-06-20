import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import mysql.connector
from db_config import DB_CONFIG_LOCALHOST  # Import the DB configuration

# Function to load and process data from MySQL database
def load_data_from_mysql():
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    query = '''
    SELECT * FROM fa_transaction  
        WHERE created_at >= CONCAT(CURDATE(), ' 00:00:00');
    '''
    df = pd.read_sql(query, connection)
    connection.close()
    df['created_at'] = pd.to_datetime(df['created_at'])
    return df

# Function to find abnormal transactions
def find_abnormal_transactions(df, minutes):
    user_transactions = defaultdict(list)

    for index, row in df.iterrows():
        user = (row["name"], row["nic"], row["payer_mobile"])
        created_at = row["created_at"]
        amount = row["paying_amount"]
        source_account = str(row["payer_account_number"]).replace(',', '').replace('.0', '')
        destination_account = str(row["final_payee_account_number"]).replace(',', '').replace('.0', '')
        status = row["status"]

        start_time = created_at - timedelta(minutes=minutes)
        user_transactions[user] = [
            (t, amt, src_acc, dest_acc, stat)
            for t, amt, src_acc, dest_acc, stat in user_transactions[user]
            if t >= start_time
        ] + [(created_at, amount, source_account, destination_account, status)]

    abnormal_users = {
        user: transactions for user, transactions in user_transactions.items() if len(transactions) >= 3
    }
    return abnormal_users

# Function to write data to another table
def write_to_rapid_trans(user, transactions_json):
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    cursor = connection.cursor()

    # Check if the record already exists in the database
    select_query = "SELECT * FROM rapid_trans WHERE user = %s AND nic = %s AND mobilenumber = %s"
    cursor.execute(select_query, (user[0], user[1], user[2]))
    existing_record = cursor.fetchone()

    if existing_record:
        # If the record exists, check if the JSON data is the same
        if existing_record[3] == transactions_json:
            # print("Record already exists in the database. Skipping insertion.")
            return
        else:
            # If JSON data is different, update the existing record
            update_query = "UPDATE rapid_trans SET myjson = %s WHERE user = %s AND nic = %s AND mobilenumber = %s"
            cursor.execute(update_query, (transactions_json, user[0], user[1], user[2]))
            # print("Updated existing record in the database.")
    else:
        # If the record doesn't exist, insert it into the database
        insert_query = "INSERT INTO rapid_trans (user, nic, mobilenumber, myjson) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (user[0], user[1], user[2], transactions_json))
        # print("Inserted new record into the database.")

    connection.commit()
    connection.close()



# Streamlit app
def main():
    df = load_data_from_mysql()

    minutes = 5  # Fixed to 5 minutes

    abnormal_transactions = find_abnormal_transactions(df, minutes)

    if abnormal_transactions:
        for user, transactions in abnormal_transactions.items():
            print(f"User: {user[0]} - NIC: {user[1]} - Phone: {user[2]}")
            transaction_df = pd.DataFrame(transactions, columns=["Timestamp", "Amount", "Source Account", "Destination Account", "Status"])

            transaction_df['Source Account'] = transaction_df['Source Account'].astype(str).replace(',', '').replace('.0', '')
            transaction_df['Destination Account'] = transaction_df['Destination Account'].astype(str).replace(',', '').replace('.0', '')

            transactions_json = transaction_df.to_json(orient="records")

            print("User Transaction Details:")
            print(transaction_df)

            write_to_rapid_trans(user, transactions_json)
    else:
        print('No abnormal transactions found.')

if __name__ == '__main__':
    main()

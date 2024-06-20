import pandas as pd
import mysql.connector
from db_config import DB_CONFIG, DB_CONFIG_LOCALHOST
from datetime import datetime, timedelta

def load_data_from_mysql():
    connection = mysql.connector.connect(**DB_CONFIG)
    
    query = '''
        SELECT t1.id, t3.name, t3.nic, DATE(t1.created_at) AS created_date, t1.device_id, t1.device_model, 
        t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
        t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
        t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
        t1.platform, t1.status
        FROM xxxxxxxxxxxxx t1
        JOIN xxxxxxxxxxxxx t2 ON t1.linked_tran_id = t2.id
        JOIN app_user t3 ON t3.username = t1.payer_id   
        AND t1.created_at >= CONCAT(CURDATE(), ' 00:00:00')
        WHERE t1.id < t2.id
    '''

    df = pd.read_sql(query, connection)
    connection.close()
    return df

def check_daily_limit(df, daily_limits, connection):
    # Merge the daily limits based on 'fund_transfer_type'
    df = df.merge(pd.DataFrame(list(daily_limits.items()), columns=['fund_transfer_type', 'daily_limit']), on='fund_transfer_type')

    # Group by user, fund_transfer_type, only_date and calculate the sum of 'paying_amount' for each group
    user_totals = df.groupby(['nic', 'fund_transfer_type', 'created_date', 'daily_limit']).agg(
        name=('name', 'first'),
        payer_email=('payer_email', 'first'),
        paying_amount=('paying_amount', 'sum')
    ).reset_index()

    # Filter users exceeding the daily limit
    users_exceeding_limit = user_totals[user_totals['paying_amount'] > user_totals['daily_limit']]

    insert_to_transaction_limits(users_exceeding_limit, connection)

def check_overall_limit(df, overall_daily_limit, connection):
    # Calculate overall daily limit for each user (identified by NIC)
    overall_sums = df.groupby(['nic', 'created_date']).agg(
        name=('name', 'first'),
        payer_email=('payer_email', 'first'),
        paying_amount=('paying_amount', 'sum')
    ).reset_index()

    overall_sums['overall_daily_limit'] = overall_daily_limit

    # Filter users exceeding overall daily limit
    users_exceeding_limit = overall_sums[overall_sums['paying_amount'] > overall_sums['overall_daily_limit']]

    insert_to_overall_transaction_limits(users_exceeding_limit, connection)

def insert_to_transaction_limits(data, connection):
    cursor = connection.cursor()
    # Fetch all NICs from the staff table
    cursor.execute('''SELECT DISTINCT nic FROM staff''')
    staff_nics = {row[0] for row in cursor.fetchall()}  # Create a set of all NICs in staff table

    for index, row in data.iterrows():
        # Check if NIC exists in the staff table
        staff_value = 'YES' if row['nic'] in staff_nics else '-'
        
        # Check if record already exists
        cursor.execute('''SELECT COUNT(*) FROM transaction_limits WHERE nic = %s AND fund_transfer_type = %s AND created_at = %s''', (row['nic'], row['fund_transfer_type'], row['created_date']))
        result = cursor.fetchone()
        
        if result[0] > 0:
            # Update existing record
            cursor.execute('''UPDATE transaction_limits SET paying_amount = %s WHERE nic = %s AND fund_transfer_type = %s AND created_at = %s''', (row['paying_amount'], row['nic'], row['fund_transfer_type'], row['created_date']))
        else:
            # Insert new record
            cursor.execute('''INSERT INTO transaction_limits (nic, name, payer_email, fund_transfer_type, paying_amount, daily_limit, created_at, staff)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (row['nic'], row['name'], row['payer_email'], row['fund_transfer_type'], row['paying_amount'], row['daily_limit'], row['created_date'], staff_value))
    connection.commit()
    cursor.close()

def insert_to_overall_transaction_limits(data, connection):
    cursor = connection.cursor()
    
    # Fetch all NICs from the staff table
    cursor.execute('''SELECT DISTINCT nic FROM staff''')
    staff_nics = {row[0] for row in cursor.fetchall()}  # Create a set of all NICs in staff table

    for index, row in data.iterrows():
        # Check if NIC exists in the staff table
        staff_value = 'YES' if row['nic'] in staff_nics else '-'

        # Check if record already exists
        cursor.execute('''SELECT COUNT(*) FROM overall_transaction_limits WHERE nic = %s AND created_at = %s''', (row['nic'], row['created_date']))
        result = cursor.fetchone()
        
        if result[0] > 0:
            # Update existing record
            cursor.execute('''UPDATE overall_transaction_limits SET paying_amount = %s WHERE nic = %s AND created_at = %s''', (row['paying_amount'], row['nic'], row['created_date']))
        else:
            # Insert new record
            cursor.execute('''INSERT INTO overall_transaction_limits (nic, name, payer_email, paying_amount, overall_daily_limit, created_at, staff)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)''', (row['nic'], row['name'], row['payer_email'], row['paying_amount'], row['overall_daily_limit'], row['created_date'], staff_value))
    connection.commit()
    cursor.close()

def main():
    # Load data from MySQL instead of CSV
    df = load_data_from_mysql()

    # Convert the 'created_at' column to datetime format
    df['created_date'] = pd.to_datetime(df['created_date'])

    # Define the daily limits
    daily_limits = {
        'CF_TO_CF': 2000000,
        'CF_TO_OTHER': 100000,
        'OTHER_TO_OTHER': 200000,
        'OTHER_TO_CF': 250000
    }

    # Define the overall daily limit
    overall_daily_limit = 2000000

    # Establish connection to localhost database
    localhost_connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)

    # Check users exceeding daily limit by fund_transfer_type
    check_daily_limit(df, daily_limits, localhost_connection)

    # Check users exceeding overall daily limit
    check_overall_limit(df, overall_daily_limit, localhost_connection)

    # Close the connection
    localhost_connection.close()

if __name__ == "__main__":
    main()

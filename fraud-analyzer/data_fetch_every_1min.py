import mysql.connector

# Database source configuration
database_source_config = {
    'host': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'port': 3306,
    'user': 'xxxxxxxxxxxxxxxxxxx',
    'password': 'xxxxxxxxxxxxx',
	'charset': 'xxxxxxxxxxxxxxx',
    'database': 'xxxxxxxxxxxxx',
}

# Establish connection to the source database
source_connection = mysql.connector.connect(
    host=database_source_config['host'],
    port=database_source_config['port'],
    user=database_source_config['user'],
    password=database_source_config['password'],
    database=database_source_config['database']
)

# Create a cursor for executing queries on the source database
source_cursor = source_connection.cursor()

# Define the SQL query to fetch data from the source table
sql_query = """
    SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
       t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
       t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
       t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
       t1.platform, t1.status
FROM transaction t1
JOIN transaction t2 ON t1.linked_tran_id = t2.id
JOIN app_user t3 ON t3.username = t1.payer_id   
WHERE t1.created_at < NOW()
AND t1.id < t2.id
"""

# Execute the SQL query on the source database
source_cursor.execute(sql_query)

# Fetch the result set
result = source_cursor.fetchall()

# Close the source cursor and connection
source_cursor.close()
source_connection.close()

# Establish connection to the target database
target_connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='cf@123',
    database='Centrix_FA'
)

# Create a cursor for executing queries on the target database
target_cursor = target_connection.cursor()

# Define the insert query for the target table
insert_query = """
    INSERT INTO fa_transaction (
        id, name, nic, created_at, device_id, device_model, 
        final_payee_account_number, final_payee_bank_name, fund_transfer_type, 
        payer_account_number, payer_bank_name, payer_email, payer_id, payer_mobile, 
        paying_amount, payment_category, payment_description, payment_processor, 
        platform, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Get the last ID in the destination table
target_cursor.execute("SELECT MAX(id) FROM fa_transaction;")
last_id = target_cursor.fetchone()[0]

# Insert fetched data into the target database if source ID is greater than last ID in destination table
for row in result:
    if row[0] > last_id:
        try:
            # Check if the ID already exists in the destination table
            target_cursor.execute("SELECT COUNT(*) FROM fa_transaction WHERE id = %s", (row[0],))
            id_count = target_cursor.fetchone()[0]
            
            if id_count == 0:  # ID does not exist in destination table, so insert the row
                target_cursor.execute(insert_query, row)
                target_connection.commit()  # Commit the transaction
        except Exception as e:
            print(f"Error inserting row: {e}")

# Close the target cursor and connection
target_cursor.close()
target_connection.close()

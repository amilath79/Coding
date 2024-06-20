import mysql.connector

# Database source configuration
database_source_config = {
    'host': 'xxxxxxxxxxxxxxxxxxxxxx',
    'port': 3306,
    'user': 'xxxxxxxxxxxxxxxxxxxxxx',
    'password': 'xxxxxxxxxxxxxxxxxxxxxx',
	'charset': 'xxxxxxxxxxxxxxxxxxxxxx',
    'database': 'xxxxxxxxxxxxxxxxxxxxxx',
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

# Define the SQL query
sql_query = """
    SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
       t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
       t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
       t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
       t1.platform, t1.status
FROM xxxxxxxxxxxxxxxxxxxxxx t1
JOIN xxxxxxxxxxxxxxxxxxxxxx t2 ON t1.linked_tran_id = t2.id
JOIN xxxxxxxxxxxxxxxxxxxxxx t3 ON t3.username = t1.payer_id   
WHERE t1.created_at >= DATE_SUB(CURDATE(), INTERVAL 7 MONTH)  -- Last 6 months
AND t1.created_at < CURDATE() - INTERVAL 1 DAY 
AND t1.id < t2.id 
AND t1.created_at NOT BETWEEN '2024-01-08' AND '2024-02-08';
"""

# Execute the SQL query on the source database
source_cursor.execute(sql_query)

# Fetch the result set
result = source_cursor.fetchall()

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
    INSERT INTO xxxxxxxxxxxxxxxxxxxxxx (
        id, name, nic, created_at, device_id, device_model, 
        final_payee_account_number, final_payee_bank_name, fund_transfer_type, 
        payer_account_number, payer_bank_name, payer_email, payer_id, payer_mobile, 
        paying_amount, payment_category, payment_description, payment_processor, 
        platform, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Insert fetched data into the target database
for row in result:
    try:
        target_cursor.execute(insert_query, row)
        target_connection.commit()  # Commit the transaction
    except Exception as e:
        print(f"Error inserting row: {e}")

# Close the cursors and connections
source_cursor.close()
source_connection.close()
target_cursor.close()
target_connection.close()

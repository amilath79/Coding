import schedule
import time
import mysql.connector

# Function to insert data into MySQL table
def my_function():
    db_config = {
        'host': 'xxxxxxxxxxxxx',
        'user': 'xxxxxxxxxxxx',
        'password': 'xxxxxxxxx',
        'database': 'xxxxxxxx',
        'port': 'xxxxx'
    }

    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Your SQL query to insert data into a table (replace 'your_table' and 'column1', 'column2', ... with actual table and column names)
    query = "INSERT INTO users (username, email, registration_date) VALUES (%s, %s, %s)"
    
    # Data to be inserted into the table
    data = ('wwww', 'wwww@gmail.com', '2023-12-15')

    # Execute the query with the data
    cursor.execute(query, data)

    # Commit the changes and close the connection
    connection.commit()
    connection.close()

    print("Data inserted successfully!")

# Schedule the function to run every 1 second (for testing purposes)
schedule.every(1).second.do(my_function)

while True:
    schedule.run_pending()
    time.sleep(1)

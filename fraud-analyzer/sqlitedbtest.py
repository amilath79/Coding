import streamlit as st
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('xxxxxxx.db')  # Replace 'your_database.db' with the actual name of your SQLite database
cursor = conn.cursor()

# Execute the SELECT query
cursor.execute('SELECT * FROM xxxxxxx')
data = cursor.fetchall()

# Close the database connection
conn.close()

# Streamlit app
st.title('Display Data from SQLite Database')

# Display the data in a Streamlit table
st.table(data)

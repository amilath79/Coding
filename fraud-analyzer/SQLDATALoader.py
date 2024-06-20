import sqlite3
import pandas as pd
import streamlit as st
from data_loader import load_global_data

# Establish SQLite connection
con = sqlite3.connect("Centrix.db")
cur = con.cursor()

def main():
    try:
        # Load data into SQLite from an external source using your data_loader function
        new_df = load_global_data()
        
        # Store the DataFrame in the SQLite database
        new_df.to_sql("xxxxxxxxxxxxxxxxxxxxxx", con, if_exists='replace', index=False, method="multi")
        
        # Execute SQL query to create a new table from the data without filtering
        cur.execute("DROP TABLE IF EXISTS xxxxxxxxxxxxxxxxxxxxxx")
        cur.execute("CREATE TABLE IF NOT EXISTS xxxxxxxxxxxxxxxxxxxxxx AS SELECT * FROM xxxxxxxxxxxxxxxxxxxxxx")
        
        # Execute SQL query to retrieve data from the newly created table
        cur.execute("SELECT * FROM CENTRIX2")
        fetched_data = cur.fetchall()
        
        # Display the fetched data using Streamlit
        st.write("Data fetched successfully")
        st.write(pd.DataFrame(fetched_data))  # Display the DataFrame in Streamlit

        df = pd.DataFrame(fetched_data)
        df.to_csv('centrix_data.csv', index=False)
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == '__main__':
    main()

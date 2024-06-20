import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

# Replace these values with your actual credentials
db_config = {
    'user': 'xxxxxxxxxxxxxxxxxxxxxx',
    'password': 'xxxxxxxxxxxxxxxxxxxxxx',
    'host': 'xxxxxxxxxxxxxxxxxxxxxx',
    'port': 'xxxxxxxxxxxxxxxxxxxxxx',
    'database': 'xxxxxxxxxxxxxxxxxxxxxx'  # Replace 'your_database_name' with your database name
}

# @st.cache
def load_data():
    try:
        engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        connection = engine.connect()
        
        df = pd.read_sql("""SELECT * FROM app_user;""", connection)

        connection.close()
        
        return df.head()  # Limiting the data to the first 5 rows

    except Exception as e:
        return f"Error while connecting to MySQL: {e}"

st.title('Display DataFrame from MySQL')

data_or_error = st.cache_data(load_data)()

if isinstance(data_or_error, pd.DataFrame):
    st.write("Data fetched successfully (First 5 rows):")
    st.dataframe(data_or_error)  # Display the DataFrame in Streamlit
else:
    st.error(data_or_error)  # Display the error message
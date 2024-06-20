# data_loader.py
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine




# Replace these values with your actual credentials
db_config = {
    'user': 'xxxxxxx',
    'password': 'xxxxxxx',
    'host': 'xxxxxxxxxxxxxxxxxxxxxxx',
    'port': 'xxxxx',
    'database': 'wwww'  # Replace 'your_database_name' with your database name
}



# def load_global_data(csv_url):
#     # Load your data into a DataFrame
#     # data = pd.read_csv(csv_url)  # Replace with your actual data loading logic
#     data = load_data()
#     return data


# @st.cache
def load_global_data():
    try:
        engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        connection = engine.connect()
        
        query = """
    SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
        t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
        t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
        t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
        t1.platform, t1.status
        FROM xxxxxxxxx t1
        JOIN xxxxxxxxxxxxxxxxxxx t2 ON t1.linked_tran_id = t2.id
        JOIN xxxxxxxxxx t3 ON t3.username = t1.payer_id   
        and t1.created_at between '2023-12-05' and '2023-12-06'
        WHERE t1.id < t2.id
            """

        # Use parameterization in the query
        df = pd.read_sql(query, connection)  # Adjust the parameters
        
        connection.close()
        
        return df  # Return the DataFrame without using head()

    except Exception as e:
        return f"Error while connecting to MySQL: {e}"





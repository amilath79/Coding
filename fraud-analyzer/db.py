import streamlit as st
import pandas as pd
import pymysql

# Function to execute MySQL query and retrieve data
def fetch_data_from_mysql(query):
    connection = pymysql.connect(
        host="xxxxxxxxxxxxxxxxxxxxxxxxxx",
        user="xxxxxxxxxx",
        password="xxxxxxxxxxxxxxxxxx",
        database="xxxxxxxxxxxxxxxxx",
        charset="xxxxxxxx",
        port = 3306,
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            return data
    finally:
        connection.close()

# Streamlit app
def main():
    st.title("Transaction Data Viewer")

    # Execute MySQL query
    query = """
    SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
             t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
             t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
             t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
             t1.platform, t1.status
    FROM xxxxxxxxxxxxxxxxxx t1
    JOIN xxxxxxxxxx t2 ON t1.linked_tran_id = t2.id
    JOIN xxxxxxxxxxxxxx t3 ON t3.username = t1.payer_id   
    WHERE t1.id < t2.id
    """

    data = fetch_data_from_mysql(query)

    # Display the data in a Streamlit table
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.warning("No data found for the specified criteria.")

if __name__ == "__main__":
    main()

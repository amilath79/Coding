import pandas as pd
import mysql.connector
import streamlit as st
from db_config import DB_CONFIG_LOCALHOST
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_login():
    if not st.session_state.get("login_status"):
        st.warning("Please log in to access this page.")
        st.stop()  # Stop further execution if not logged in

# Function to retrieve data from MySQL tables
def retrieve_data_from_mysql():
    try:
        # Connect to the database
        localhost_connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = localhost_connection.cursor(dictionary=True)

        # Get the current date
        current_date = datetime.now().date()
        
        # Execute queries to retrieve data from the tables
        cursor.execute("SELECT * FROM xxxxxxxxxxxxxxxxxxxxxx WHERE DATE(created_at) = %s ORDER BY created_at DESC", (current_date,))
        transaction_limits_data = cursor.fetchall()
        
        cursor.execute("SELECT * FROM xxxxxxxxxxxxxxxxxxxxxx WHERE DATE(created_at) = %s ORDER BY created_at DESC", (current_date,))
        overall_transaction_limits_data = cursor.fetchall()
        
        return transaction_limits_data, overall_transaction_limits_data
    
    except mysql.connector.Error as err:
        st.error(f"Error accessing MySQL: {err.msg}")
        st.error(f"Error code: {err.errno}")
        st.error(f"Error details: {err}")
        return None, None
    
# Function to format paying_amount column with commas
def daily_format_data(data):
    for row in data:
        row['paying_amount'] = '{:,.2f}'.format(float(row['paying_amount']))
        row['daily_limit'] = '{:,.2f}'.format(float(row['daily_limit']))
    return data

def overall_format_data(data):
    for row in data:
        row['paying_amount'] = '{:,.2f}'.format(float(row['paying_amount']))
        row['overall_daily_limit'] = '{:,.2f}'.format(float(row['overall_daily_limit']))
    return data

# Function to check if ID exists in noc_escalated_ids table
def check_id_existence(row_id):
    try:
        localhost_connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = localhost_connection.cursor()

        cursor.execute("SELECT * FROM noc_escalated_ids WHERE case_id = %s", (row_id,))
        result = cursor.fetchone()
        return result is not None

    except mysql.connector.Error as err:
        st.error(f"Error checking ID existence in database: {err.msg}")
        st.error(f"Error code: {err.errno}")
        st.error(f"Error details: {err}")
        return False

# Function to send email and insert ID into the database
def send_email_and_insert_id(row_id):
    sender_email = "dilshanworkplace@gmail.com"
    receiver_email = "dilshansr@cf.lk"
    password = "pkht wiwd zqkr fqrx"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Escalation Required"

    # body = f"Record with ID {row_id} needs attention."
    body = f"Record with ID {row_id} needs attention. Please use the link below : xxxxxxxxxxxxxxxxxxxxxx{row_id}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(".gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)

    # Insert row_id into noc_escalated_ids table
    try:
        localhost_connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = localhost_connection.cursor()

        cursor.execute("INSERT INTO xxxxxxxxxxxxxxxxxxxxxx (case_id) VALUES (%s)", (row_id,))
        localhost_connection.commit()

    except mysql.connector.Error as err:
        st.error(f"Error inserting ID into database: {err.msg}")
        st.error(f"Error code: {err.errno}")
        st.error(f"Error details: {err}")

# Streamlit UI
def main():
    check_login()
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Daily Transaction Limits Checker</h1>", unsafe_allow_html=True)
    
    # Retrieve data from MySQL
    transaction_limits_data, overall_transaction_limits_data = retrieve_data_from_mysql()

    # Define custom CSS style for table font size
    table_style = """
        <style>
            table {
                font-size: 14px;
            }

            .highlight {
                background-color: yellow !important;
                color: black !important;
            }
        </style>
    """

    # Define fund transfer types
    fund_transfer_types = ['CF_TO_CF', 'CF_TO_OTHER', 'OTHER_TO_OTHER', 'OTHER_TO_CF']
    
    # Display the retrieved data for each fund transfer type
    for fund_transfer_type in fund_transfer_types:
        st.markdown(f"<h1 style='text-align: left; font-size: 25px;'>Transaction Limits for {fund_transfer_type}</h1>", unsafe_allow_html=True)
        st.markdown(table_style, unsafe_allow_html=True)
        filtered_data = [row for row in transaction_limits_data if row['fund_transfer_type'] == fund_transfer_type]
        if filtered_data:
            formatted_data = daily_format_data(filtered_data)
            df = pd.DataFrame(formatted_data)

            # Add "Escalate" button to each row if ID doesn't exist in noc_escalated_ids table
            for index, row in df.iterrows():
                if not check_id_existence(row['id']):
                    # Generate a unique key based on the row index and fund transfer type
                    button_key = f"escalate_{index}_{fund_transfer_type}"
                    if st.button(f"Escalate {row['id']}", key=button_key):
                        send_email_and_insert_id(row['id'])  # Pass the row ID to the email sending and ID insertion function

            df_style = df.style.apply(lambda row: ['background: #d1de6f; color: black']*len(row) if row['staff'] == 'YES' else ['']*len(row), axis=1)
            st.table(df_style)
        else:
            st.markdown(table_style, unsafe_allow_html=True)
            st.write(f"No data available for {fund_transfer_type} daily transaction limits.")


    if overall_transaction_limits_data:
        overall_formated_data = overall_format_data(overall_transaction_limits_data)
        st.markdown(f"<h1 style='text-align: left; font-size: 25px;'>Overall Transaction Limits</h1>", unsafe_allow_html=True)
        overall_df = pd.DataFrame(overall_formated_data)
        overall_df_style = overall_df.style.apply(lambda row: ['background: #d1de6f; color: black']*len(row) if row['staff'] == 'YES' else ['']*len(row), axis=1)
        st.table(overall_df_style)
    else:
        st.markdown(f"<h1 style='text-align: left; font-size: 25px;'>Overall Transaction Limits</h1>", unsafe_allow_html=True)
        st.markdown(table_style, unsafe_allow_html=True)
        st.write("No data available for overall transaction limits.")

if __name__ == "__main__":
    main()
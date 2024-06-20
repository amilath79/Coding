

import pandas as pd
import streamlit as st
import datetime
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_config import DB_CONFIG_LOCALHOST  # Import the DB configuration

# Function to load data from MySQL database
def load_data_from_mysql():
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    today = datetime.date.today()
    query = f"SELECT * FROM rapid_trans WHERE DATE(time) = '{today}'"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Function to check if ID is escalated
def is_escalated(row_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM rapid_trans_ecalated_id WHERE case_id = %s", (row_id,))
        result = cursor.fetchone()
        connection.close()
        return result is not None
    except mysql.connector.Error as err:
        st.error(f"Error checking escalation status: {err.msg}")
        st.error(f"Error code: {err.errno}")
        st.error(f"Error details: {err}")
        return False

# Function to send email and insert ID into noc_escalated_ids table
def send_email_and_insert_id(row_id):
    sender_email = "dilshanworkplace@gmail.com"
    receiver_email = "rajithamsc@cf.lk"
    password = "pkht wiwd zqkr fqrx"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Escalation Required"

    # body = f"Record with ID {row_id} need attention at Rapid Transactions."
    body = f"Record with ID {row_id} needs attention. Please use the link below : http://3.22.119.88:8501/?page=Actions&caseID={row_id}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)

    # Insert row_id into noc_escalated_ids table
    try:
        localhost_connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = localhost_connection.cursor()

        cursor.execute("INSERT INTO rapid_trans_ecalated_id (case_id) VALUES (%s)", (row_id,))
        localhost_connection.commit()
        st.success(f"Record with ID {row_id} Case Escalated successfully")
    except mysql.connector.Error as err:
        st.error(f"Error inserting ID into database: {err.msg}")
        st.error(f"Error code: {err.errno}")
        st.error(f"Error details: {err}")

# Streamlit app
# Streamlit app
# Streamlit app
# Streamlit app
def main():
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Rapid Transactions Detector</h1>", unsafe_allow_html=True)
    st.markdown("This analyzer uncovers users with an abnormal number of transactions within a short period by continuously monitoring live transactions in Centrix.")

    # Load data
    df = load_data_from_mysql()

    # Display data
    if not df.empty:
        for index, user in df.iterrows():
            st.markdown(
                f"""
                <div style='border: 1px solid #e6e6e6; border-radius: 5px; padding: 10px;'>
                    <p>Name: {user['user']} - NIC: {user['nic']} - Phone: {user['mobilenumber']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Create an Escalate button for each row
            if not is_escalated(user['id']):
                if st.button(f"Escalate ({user['id']})"):
                    # Perform escalation action here
                    send_email_and_insert_id(user['id'])
            else:
                st.write(f"Escalate ({user['id']}) - Already escalated")
                
            # Remove commas from "Source Account" and "Destination Account" fields in JSON data
            transactions = pd.read_json(user['myjson'])
            transactions["Source Account"] = transactions["Source Account"].astype(str).str.replace(",", "")
            transactions["Destination Account"] = transactions["Destination Account"].astype(str).str.replace(",", "")
            st.write("User Transaction Details:")
            st.write(transactions)
            st.write("----------------------------")
    else:
        st.write('No data available.')

if __name__ == '__main__':
    main()

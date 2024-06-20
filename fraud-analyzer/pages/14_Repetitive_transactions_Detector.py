import pandas as pd
import streamlit as st
import mysql.connector
from db_config import DB_CONFIG_LOCALHOST
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to load data from MySQL database for today's records
def load_data_from_mysql():
    try:
        connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        today_date = datetime.now().date()  # Get today's date
        query = "SELECT * FROM repettive_trans WHERE DATE(time) = %s"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (today_date,))
        data = cursor.fetchall()
        connection.close()
        return data
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Function to check if the record has been escalated
def is_escalated(row_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM repettive_trans_ecalated_id WHERE case_id = %s", (row_id,))
        result = cursor.fetchone()
        connection.close()
        return result is not None
    except mysql.connector.Error as err:
        st.error(f"Error checking escalation status: {err.msg}")
        st.error(f"Error code: {err.errno}")
        st.error(f"Error details: {err}")
        return False


# Function to send email and insert ID into the database
def send_email_and_insert_id(row_id):
    sender_email = "dilshanworkplace@gmail.com"
    receiver_email = "rajithamsc@cf.lk"
    password = "pkht wiwd zqkr fqrx"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Escalation Required"

    body = f"Record with ID {row_id} needs attention. Please use the link below : http://3.22.119.88:8501/?page=Actions&caseID={row_id}"
    # body = f"Record with ID {row_id} needs attention in Repettive transactions."
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)

    # Insert row_id into repettive_trans_ecalated_id table
    try:
        localhost_connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = localhost_connection.cursor()

        cursor.execute("INSERT INTO repettive_trans_ecalated_id (case_id) VALUES (%s)", (row_id,))
        localhost_connection.commit()

        st.success(f"Record with ID {row_id} Case Escalated successfully")
    except mysql.connector.Error as err:
        st.error(f"Error inserting ID into database: {err.msg}")
        st.error(f"Error code: {err.errno}")
        st.error(f"Error details: {err}")

# Streamlit app
def main():

    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Repetitive Transactions Detector</h1>", unsafe_allow_html=True)
    st.markdown("Uncover the repetitive transactions cluster for the same final payee account and the same amount within a short period by continuously monitoring live transactions in Centrix.")
   

    # Load data for today's records
    data = load_data_from_mysql()

    # Display data
    if data:
        for row in data:
            # Display transaction details
            # st.write(f"Name: {row['name']} - NIC: {row['nic']} - Transaction Count: {row['count']} - Amount: {row['amount']}")
            st.markdown(
                    f"""
                    <div style='border: 1px solid #e6e6e6; border-radius: 5px; padding: 10px;'>
                        <p>Name: {row['name']} - NIC: {row['nic']} - Transaction Count: {row['count']} - Amount: {row['amount']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            transactions = pd.read_json(row['json'])
            st.write("Transactions:")
            st.write(transactions)

            # Check if the record has been escalated
            escalated = is_escalated(row['id'])

            # Add an Escalate button next to the transaction details if not already escalated
            if not escalated:
                if st.button(f"Escalate Cause {row['id']}"):
                    send_email_and_insert_id(row['id'])
            else:
                st.write("This cause has already been escalated.")
            
            st.write("----------------------------")
    else:
        st.write('No repetitive transactions available for today.')

if __name__ == '__main__':
    main()

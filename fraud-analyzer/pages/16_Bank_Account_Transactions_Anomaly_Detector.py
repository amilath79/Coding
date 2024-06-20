import streamlit as st
import pandas as pd
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_config import DB_CONFIG_LOCALHOST

def load_data_from_mysql():
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bank_acc_anomaly")
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def escalate_anomaly(anomaly_id):
    send_email_and_insert_id(anomaly_id)

# Function to send email and insert ID into the database
def send_email_and_insert_id(row_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = connection.cursor()

        # Check if case ID already exists in bankacc_escalated_ids table
        cursor.execute("SELECT * FROM bankacc_escalated_ids WHERE case_id = %s", (row_id,))
        result = cursor.fetchone()
        if not result:
            sender_email = "dilshanworkplace@gmail.com"
            receiver_email = "damikads@cf.lk"
            password = "pkht wiwd zqkr fqrx"

            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = "Escalation Required"

            body = f"Record with ID {row_id} needs attention."
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password)
                text = message.as_string()
                server.sendmail(sender_email, receiver_email, text)

            # Insert case ID into bankacc_escalated_ids table
            cursor.execute("INSERT INTO bankacc_escalated_ids (case_id) VALUES (%s)", (row_id,))
            connection.commit()

            # Show success message
            st.success("Email has been successfully sent for this anomaly.")
        else:
            # Show warning message
            st.warning("Email has already been sent for this anomaly.")

    except mysql.connector.Error as err:
        st.error(f"Error inserting ID into database: {err.msg}")

# Load data from MySQL
data = load_data_from_mysql()

# Organize data into a dictionary with names and corresponding dates and myjson
organized_data = {}
for row in data:
    anomaly_id = row['anomalyID']
    name_nic = f"Anomaly ID: {anomaly_id}, Name: {row['name']}, NIC: {row['nic']}"
    if name_nic not in organized_data:
        organized_data[name_nic] = []
    organized_data[name_nic].append({'date': row['date'], 'myjson': row['myjson'], 'anomaly_id': anomaly_id})

# Display data in Streamlit
st.title('Bank Account Anomaly Data')
st.markdown("This analysis identifies the newly added accounts with unusual transaction patterns for new final payee bank names in Centrix by continuously monitoring live transactions. Moreover, it raises alerts, highlighting potential anomalies that should be addressed immediately.")


if not organized_data:
    st.write('No data available.')
else:
    for name_nic, entries in organized_data.items():
        with st.expander(name_nic):
            for entry in entries:
                myjson = entry['myjson']
                myjson_dict = eval(myjson)  # Convert JSON string to dictionary
                st.write(pd.DataFrame.from_dict(myjson_dict, orient='index').transpose())
                st.write(f"Date: {entry['date']}")
                button_key = f"Escalate_{entry['anomaly_id']}"  # Unique key for the button
                if st.button(f"Escalate {entry['anomaly_id']}", key=button_key):
                    escalate_anomaly(entry['anomaly_id'])

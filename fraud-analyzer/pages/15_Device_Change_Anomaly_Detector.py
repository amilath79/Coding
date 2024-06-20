import streamlit as st
import mysql.connector
import json
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_config import DB_CONFIG_LOCALHOST

# Function to retrieve data from the database
def retrieve_data_from_db():
    connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
    cursor = connection.cursor()
    cursor.execute("SELECT anomalyID, name, nic, myjson, date_time FROM device_change_anomaly")
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

# Function to send email and insert ID into the database
def send_email_and_insert_id(row_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = connection.cursor()

        # Check if case ID already exists in device_escalated_ids table
        cursor.execute("SELECT * FROM device_escalated_ids WHERE case_id = %s", (row_id,))
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

            # Insert case ID into device_escalated_ids table
            cursor.execute("INSERT INTO device_escalated_ids (case_id) VALUES (%s)", (row_id,))
            connection.commit()

            st.success("Email has been successfully sent for this anomaly.")
        else:
            st.warning("Email has already been sent for this anomaly.")

    except mysql.connector.Error as err:
        st.error(f"Error inserting ID into database: {err.msg}")

# Main Streamlit app
def main():
    st.title("Device Change Anomaly Detector")
    st.markdown("Device-specific transaction analysis aims to uncover newly added devices in Centrix by continuously monitoring live transactions. Simultaneously, it displays the possibility of anomalies for immediate investigation.")

    # Retrieve data from the database
    anomalies_data = retrieve_data_from_db()

    # Track encountered anomaly IDs
    encountered_ids = set()

    # Display data
    if anomalies_data:
        for anomaly_id, name, nic, myjson, date_time in anomalies_data:
            if anomaly_id not in encountered_ids:
                encountered_ids.add(anomaly_id)
                key = f"Anomaly ID: {anomaly_id} - Last Device Change for {name} ({nic}) - {date_time}"
                dropdown_expander = st.expander(key)
                with dropdown_expander:
                    st.write("Anomaly ID:", anomaly_id)
                    st.write(f"Name: {name}, NIC: {nic}")
                    myjson_dict = json.loads(myjson)
                    df = pd.DataFrame(list(myjson_dict.items()), columns=["Key", "Value"])
                    st.table(df)
                    st.write(f"Date: {date_time}")
                    button_key = f"escalate_button_{anomaly_id}"  # Unique key for the button
                    if st.button("Escalate", key=button_key):
                        send_email_and_insert_id(anomaly_id)
    else:
        st.write("No anomalies found.")

if __name__ == '__main__':
    main()

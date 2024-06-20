import pandas as pd
import streamlit as st
import mysql.connector
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mysql.connector import Error
from db_config import DB_CONFIG_LOCALHOST

def fetch_anomalies_from_mysql():
    anomalies = []
    try:
        connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = connection.cursor(dictionary=True)
        current_date = datetime.date.today()

        cursor.execute("SELECT * FROM tran_Amount_anomalies WHERE DATE(Created_At) = %s", (current_date,))
        anomalies = cursor.fetchall()

    except Error as e:
        st.error(f"Error fetching anomalies from MySQL: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return anomalies

def display_anomalies(anomalies):
    for anomaly in anomalies:
        with st.expander(f"Anomaly Transaction Detected - ID: {anomaly['ID']}"):
            st.text(f'''Name: {anomaly['Name']}
NIC: {anomaly['NIC']}
Paying Amount: {anomaly['Paying_Amount']}
Created At: {anomaly['Created_At']}
Mobile No: {anomaly['Mobile_No']} ''')

            st.markdown("<h2 style='text-align: Left; font-size: 20px;'>User Transaction History:</h2>", unsafe_allow_html=True)
            
            user_transaction_history_df = pd.read_json(anomaly['User_Transaction_History'])

            if 'Transaction Date' in user_transaction_history_df:
                user_transaction_history_df['Transaction Date'] = pd.to_datetime(user_transaction_history_df['Transaction Date'], unit='ms') 

            st.write(user_transaction_history_df)

            st.markdown("<h2 style='text-align: Left; font-size: 20px;'>Conclusion : </h2>", unsafe_allow_html=True)
            st.write(anomaly['Conclusion'])
            st.write("\n")

def check_id_existence(row_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM noc_escalated_ids WHERE case_id = %s", (row_id,))
        result = cursor.fetchone()
        return result is not None

    except mysql.connector.Error as err:
        st.error(f"Error checking ID existence in database: {err.msg}")
        return False

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def send_email_and_insert_id(row_id):
    sender_email = "dilshanworkplace@gmail.com"
    receiver_email = "dilshansr@cf.lk"
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

    try:
        connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = connection.cursor()

        cursor.execute("INSERT INTO noc_escalated_ids (case_id) VALUES (%s)", (row_id,))
        connection.commit()

    except mysql.connector.Error as err:
        st.error(f"Error inserting ID into database: {err.msg}")

def main():

    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Transaction Amount Anomaly Detector</h1>", unsafe_allow_html=True)
    st.markdown("This analysis promptly spots outlier transactions in Centrix by continuously monitoring live transactions. Simultaneously, it raises alerts, highlighting potential anomalies for immediate attention.")

    anomalies = fetch_anomalies_from_mysql()

    for anomaly in anomalies:
        if not check_id_existence(anomaly['ID']):
            button_key = f"escalate_{anomaly['ID']}"
            if st.button(f"Escalate {anomaly['ID']}", key=button_key):
                send_email_and_insert_id(anomaly['ID'])

    display_anomalies(anomalies)

if __name__ == '__main__':
    main()

import streamlit as st
import pymysql
from datetime import datetime
from db_config import DB_CONFIG_LOCALHOST

# Importing email related libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Mapping dictionary for column names
COLUMN_DISPLAY_NAMES = {
    'id': 'Case ID',
    'nic': 'NIC',
    'name': 'Name',
    'payer_email': 'Email',
    'fund_transfer_type': 'Transfer Type',
    'paying_amount': 'Amount',
    'daily_limit': 'Daily Limit',
    'created_at': 'Date',
    'staff': 'Staff'
}

ANOMALY_COLUMN_DISPLAY_NAMES = {
    'U_ID': 'Case ID',
    'ID': 'NIC',
    'Name': 'Name',
    'NIC': 'Mobile No',
    'Paying_Amount': 'Amount',
    'Created_At': 'Date'
}

CASE_LOG_COLUMN_DISPLAY_NAMES = {
    'case_id': 'Case ID',
    'digital_manager': 'Digital Manager',
    'digital_manager_comment': 'Digital Manager Comment',
    'digital_manager_status': 'Digital Manager Status',
    'head_of_Digital_&_fintech': 'Head of Digital & Fintech',
    'head_comment': 'Head of Digital & Fintech Comment',
    'head_status': 'Head of Digital & Fintech Status',
    'final_status' : 'Final Status'
}

# Function to connect to the database
def connect_to_db():
    conn = pymysql.connect(**DB_CONFIG_LOCALHOST)
    return conn

# Function to execute SQL query to get column names
def get_column_names(table_name):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SHOW COLUMNS FROM {}".format(table_name))
    column_names = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return column_names

# Function to execute SQL query to fetch data
def execute_query(query, args=(), fetchall=False):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query, args)
    if fetchall:
        result = cur.fetchall()
    else:
        result = cur.fetchone()
    cur.close()
    conn.close()
    return result

# Function to retrieve name and staff from transaction_limits table
def get_additional_data(case_id):
    query = "SELECT name, staff FROM transaction_limits WHERE id = %s"
    result = execute_query(query, (case_id,))
    return result

# Function to insert data into transaction_limits_case_log table
def insert_case_log_DM(case_id, name, staff, digital_manager_comment, digital_manager_status, final_status='Investigating'):
    conn = connect_to_db()
    cur = conn.cursor()

    # Get current timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert data into transaction_limits_case_log table
    query = "INSERT INTO transaction_limits_case_log (case_id, name, staff, digital_manager, digital_manager_comment, digital_manager_status, final_status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cur.execute(query, (case_id, name, staff, 'YES', digital_manager_comment, digital_manager_status, final_status))

    if digital_manager_status == 'Closed':
        send_email('Case Closed', f'The case with ID {case_id} has been closed. Comment - {digital_manager_comment}', 'dilshansr@cf.lk')

    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()

def insert_case_log_HDF(case_id, name, staff, head_comment, head_status, final_status='Investigating'):
    conn = connect_to_db()
    cur = conn.cursor()

    # Get current timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert data into transaction_limits_case_log table
    query = """
    INSERT INTO transaction_limits_case_log (case_id, name, staff, `head_of_Digital_&_fintech`, head_comment, head_status, final_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    staff = VALUES(staff),
    `head_of_Digital_&_fintech` = VALUES(`head_of_Digital_&_fintech`),
    head_comment = VALUES(head_comment),
    head_status = VALUES(head_status),
    final_status = VALUES(final_status)
    """
    cur.execute(query, (case_id, name, staff, 'YES', head_comment, head_status, final_status))

    if head_status == 'Closed':
        send_email('Case Closed', f'The case with ID {case_id} has been closed. Comment - {head_comment}', 'dilshansr@cf.lk')

    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()

# Function to insert data into transaction_limits_case_log table
def insert_case_log_Comp(case_id, name, staff, compliance_comment, compliance_status, final_status='Investigating'):
    conn = connect_to_db()
    cur = conn.cursor()

    # Get current timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert data into transaction_limits_case_log table
    query = """
    INSERT INTO transaction_limits_case_log 
    (case_id, name, staff, compliance, compliance_comment, compliance_status, final_status) 
    VALUES (%s, %s, %s, %s, %s, %s, %s) 
    ON DUPLICATE KEY UPDATE 
    name = VALUES(name), 
    staff = VALUES(staff), 
    compliance = VALUES(compliance), 
    compliance_comment = VALUES(compliance_comment), 
    compliance_status = VALUES(compliance_status), 
    final_status = VALUES(final_status)
    """
    cur.execute(query, (case_id, name, staff, 'YES', compliance_comment, compliance_status, final_status))

    if compliance_status == 'Closed':
        send_email('Case Closed', f'The case with ID {case_id} has been closed. Comment - {compliance_comment}', 'dilshansr@cf.lk')
    
    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()

# Function to retrieve data from transaction_limits_case_log table
def get_case_log(case_id):
    conn = connect_to_db()
    cur = conn.cursor()

    # Query data from transaction_limits_case_log table
    query = "SELECT case_id, digital_manager, digital_manager_comment, digital_manager_status, final_status FROM xxxxxxxxxxxxxxxxxxxxxx WHERE case_id = %s"
    cur.execute(query, (case_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        # Get column names
        column_names = ['case_id', 'digital_manager', 'digital_manager_comment', 'digital_manager_status', 'final_status']
        
        # Convert values to text format and use display names
        result_text = {CASE_LOG_COLUMN_DISPLAY_NAMES[col_name]: str(value) for col_name, value in zip(column_names, result)}
        return result_text
    else:
        return None
    
# Function to retrieve data from transaction_amount_anomaly_case_log table
def get_amount_anomaly_case_log(case_id):
    conn = connect_to_db()
    cur = conn.cursor()

    # Query data from transaction_limits_case_log table
    query = "SELECT case_id, digital_manager, digital_manager_comment, digital_manager_status, final_status FROM xxxxxxxxxxxxxxxxxxxxxx WHERE case_id = %s"
    cur.execute(query, (case_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        # Get column names
        column_names = ['case_id', 'digital_manager', 'digital_manager_comment', 'digital_manager_status', 'final_status']
        
        # Convert values to text format and use display names
        result_text = {CASE_LOG_COLUMN_DISPLAY_NAMES[col_name]: str(value) for col_name, value in zip(column_names, result)}
        return result_text
    else:
        return None

# Function to send email
def send_email(subject, body, recipient):
    # Email credentials and settings
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'xxxxxxxxxxxxxxxxxxxxxx@gmail.com'
    sender_password = 'xxxxxxxxxxxxxxxxxxxxxx'

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    # Attach body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Create SMTP session
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())

# Function to get the case_id from the query parameters
def get_case_id():
    query_params = st.experimental_get_query_params()
    caseID = query_params.get('caseID', [''])[0]
    return caseID

# Get the case_id from the URL
caseID = get_case_id()

# Streamlit app
def main(caseID):
    st.title('Transaction Limits Dashboard')

    # Initialize session state
    if 'case_id' not in st.session_state:
        st.session_state.case_id = None
    
    # Create the catogary dropdown menu
    options = ['Transaction Limits', 'Transaction Amount Anomaly', 'Transaction Time Anomaly', 'Rapid Transactions', 'Repetitive Transactions']
    cat_selected_option = st.selectbox('Choose:', options)

    caseID = get_case_id()

    # Search box for ID
    search_id = st.text_input('Search by ID', value=caseID)

    # Retrieve data related to the searched ID
    if st.button('Search'):
        if cat_selected_option == 'Transaction Limits':    
            if search_id:
                query = "SELECT * FROM xxxxxxxxxxxxxxxxxxxxxx WHERE id = %s ORDER BY created_at DESC"
                result = execute_query(query, (search_id,))
                if result:
                    st.session_state.case_id = search_id
                    st.subheader('Data related to ID: {}'.format(search_id))
                    # Get column names dynamically from the database table
                    column_names = get_column_names("transaction_limits")
                    # Display data in a vertical table
                    col1, col2 = st.columns(2)
                    for col_name, value in zip(column_names, result):
                        with col1:
                            st.write(COLUMN_DISPLAY_NAMES.get(col_name, col_name))  # Lookup display name
                        with col2:
                            st.write(str(value))  # Convert value to string

            # Display data from transaction_limits_case_log table
            if st.session_state.case_id:
                case_log_data = get_case_log(st.session_state.case_id)
                if case_log_data:
                    st.subheader('Case Log Data')
                    col1, col2 = st.columns(2)
                    for col_name, value in case_log_data.items():
                        with col1:
                            st.write(col_name)  # Display column name
                        with col2:
                            st.write(value)  # Display value

        elif cat_selected_option == 'Transaction Amount Anomaly':    
            if search_id:
                query = "SELECT ID, NIC, Name, Mobile_No, Paying_Amount, Created_At FROM xxxxxxxxxxxxxxxxxxxxxx WHERE ID = %s ORDER BY created_at DESC"
                result = execute_query(query, (search_id,))
                if result:
                    st.session_state.case_id = search_id
                    st.subheader('Data related to ID: {}'.format(search_id))
                    # Get column names dynamically from the database table
                    column_names = get_column_names("tran_Amount_anomalies")
                    # Display data in a vertical table
                    col1, col2 = st.columns(2)
                    for col_name, value in zip(column_names, result):
                        with col1:
                            st.write(ANOMALY_COLUMN_DISPLAY_NAMES.get(col_name, col_name))  # Lookup display name
                        with col2:
                            st.write(str(value))  # Convert value to string

            # Display data from transaction_amount_anomaly_case_log table
            if st.session_state.case_id:
                case_log_data = get_amount_anomaly_case_log(st.session_state.case_id)
                if case_log_data:
                    st.subheader('Case Log Data')
                    col1, col2 = st.columns(2)
                    for col_name, value in case_log_data.items():
                        with col1:
                            st.write(col_name)  # Display column name
                        with col2:
                            st.write(value)  # Display value
        else:
            st.write('No Such Table')

    # Text box for comments
    comments = st.text_area('Comments')

    # Retrieve query parameters
    query_params = st.experimental_get_query_params()

    # Get selected_option from query parameters if available
    selected_option = query_params.get("selected_option", [None])[0]
    escalate_selected_option = query_params.get("escalate_selected_option", [None])[0]

    # Create the first dropdown menu
    options = ['Digital Manager', 'Head of Digital & Fintech', 'Compliance']
    selected_option = st.selectbox('Choose an option:', options, index=options.index(selected_option) if selected_option in options else 0, disabled=True)

    # Update the options of the second dropdown based on the selection of the first dropdown
    if selected_option == 'Digital Manager':
        escalate_options = ['Head of Digital & Fintech']
    elif selected_option == 'Head of Digital & Fintech':
        escalate_options = ['Compliance']
    elif selected_option == 'Compliance':
        escalate_options = ['CBSL/FIU']
    else:
        escalate_options = ['Digital Manager', 'Head of Digital & Fintech', 'Compliance']

    # Button for case actions
    if st.button('Case Close'):

        if selected_option == 'Digital Manager':
            # message = 'Digital Manager'
            # st.write(message)

            # Logic to handle case close action
            case_id = st.session_state.case_id
            if case_id:
                comment = comments
                # Get additional data (name and staff) from transaction_limits table
                name, staff = get_additional_data(case_id)
                if name and staff:
                    # Insert the log with 'Closed' status
                    insert_case_log_DM(case_id, name, staff, comment, 'Closed', 'Closed')
                    st.write('Case Closed!')
                    # Clear text input and text area
                    search_id = ''
                    comments = ''
                else:
                    st.error('No data found for the case ID')
            else:
                st.error('No case loaded')

        elif selected_option == 'Head of Digital & Fintech':
            # message = 'Head of Digital & Fintech'
            # st.write(message)

            # Logic to handle case close action
            case_id = st.session_state.case_id
            if case_id:
                comment = comments
                # Get additional data (name and staff) from transaction_limits table
                name, staff = get_additional_data(case_id)
                if name and staff:
                    # Insert the log with 'Closed' status
                    insert_case_log_HDF(case_id, name, staff, comment, 'Closed', 'Closed')
                    st.write('Case Closed!')
                    # Clear text input and text area
                    search_id = ''
                    comments = ''
                else:
                    st.error('No data found for the case ID')
            else:
                st.error('No case loaded')

        elif selected_option == 'Compliance':
            # message = 'compliance'
            # st.write(message)

            # Logic to handle case close action
            case_id = st.session_state.case_id
            if case_id:
                comment = comments
                # Get additional data (name and staff) from transaction_limits table
                name, staff = get_additional_data(case_id)
                if name and staff:
                    # Insert the log with 'Closed' status
                    insert_case_log_Comp(case_id, name, staff, comment, 'Closed', 'Closed')
                    st.write('Case Closed!')
                    # Clear text input and text area
                    search_id = ''
                    comments = ''
                else:
                    st.error('No data found for the case ID')
            else:
                st.error('No case loaded')

    
    # Create the second dropdown menu
    escalate_selected_option = st.selectbox('Case Escalate to:', escalate_options, index=escalate_options.index(escalate_selected_option) if escalate_selected_option in escalate_options else 0, disabled=True)

    # Update the query parameters in the URL
    new_params = {"page": "Actions", "caseID": search_id, "selected_option": selected_option}
    st.experimental_set_query_params(**new_params)

    if st.button('Case Escalated to Next Level'):

        if escalate_selected_option == 'Head of Digital & Fintech':
            # message = 'head_of_Digital_&_fintech'
            # st.write(message)

            # Logic to handle case escalation action
            case_id = st.session_state.case_id
            if case_id:
                comment = comments
                # Get additional data (name and staff) from transaction_limits table
                name, staff = get_additional_data(case_id)
                if name and staff:
                    # Insert the log with 'Escalated' status
                    insert_case_log_DM(case_id, name, staff, comment, 'Escalated')
                    # Update final_status to 'Investigating'
                    conn = connect_to_db()
                    cur = conn.cursor()
                    cur.execute("UPDATE transaction_limits_case_log SET final_status = 'Investigating' WHERE case_id = %s", (case_id,))
                    conn.commit()
                    conn.close()
                    send_email('Case Escalation', f'The case with ID {case_id} has been escalated. Comment - {comment}. Please use the link below : http:/xxxxxxxxxxxxxxxxxxxxxx={case_id}&xxxxxxxxxxxxxxxxxxxxxx', 'xxxxxxxxxxxxxxxxxxxxxx@')
                    st.write('Case Escalated to Next Level!')
                else:
                    st.error('No data found for the case ID')
            else:
                st.error('No case loaded')

        elif escalate_selected_option == 'Compliance':
            # message = 'compliance'
            # st.write(message)

            # Logic to handle case escalation action
            case_id = st.session_state.case_id
            if case_id:
                comment = comments
                # Get additional data (name and staff) from transaction_limits table
                name, staff = get_additional_data(case_id)
                if name and staff:
                    # Insert the log with 'Escalated' status
                    insert_case_log_HDF(case_id, name, staff, comment, 'Escalated')
                    # Update final_status to 'Investigating'
                    conn = connect_to_db()
                    cur = conn.cursor()
                    cur.execute("UPDATE transaction_limits_case_log SET final_status = 'Investigating' WHERE case_id = %s", (case_id,))
                    conn.commit()
                    conn.close()
                    send_email('Case Escalation', f'The case with ID {case_id} has been escalated. Comment - {comment}. Please use the link below : http://3.xxxxxxxxxxxxxxxxxxxxxx={case_id}&selected_option=Compliance', 'xxxxxxxxxxxxxxxxxxxxxx')
                    st.write('Case Escalated to Next Level!')
                else:
                    st.error('No data found for the case ID')
            else:
                st.error('No case loaded')

        elif escalate_selected_option == 'CBSL/FIU':
            # message = 'CBSL/FIU'
            # st.write(message)

            # Logic to handle case escalation action
            case_id = st.session_state.case_id
            if case_id:
                comment = comments
                # Get additional data (name and staff) from transaction_limits table
                name, staff = get_additional_data(case_id)
                if name and staff:
                    # Insert the log with 'Escalated' status
                    insert_case_log_Comp(case_id, name, staff, comment, 'Escalated')
                    # Update final_status to 'Investigating'
                    conn = connect_to_db()
                    cur = conn.cursor()
                    cur.execute("UPDATE transaction_limits_case_log SET final_status = 'Investigating' WHERE case_id = %s", (case_id,))
                    conn.commit()
                    conn.close()
                    send_email('Case Escalation', f'The case with ID {case_id} has been escalated. Comment - {comment}', 'xxxxxxxxxxxxxxxxxxxxxx')
                    st.write('Case Escalated to Next Level!')
                else:
                    st.error('No data found for the case ID')
            else:
                st.error('No case loaded')


if __name__ == '__main__':
    main(caseID)

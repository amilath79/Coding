import streamlit as st
import Daily_Transaction_Limits_Checker, Actions, Daily_Transaction_Limits_Reports, Transaction_Amount_Anomaly_Detector, Transaction_Time_Anomaly_Detector
import Transaction_Limits_Information
import contact
import homepage
from pages import home

# Function to display navigation buttons in the sidebar
def display_navigation():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        st.experimental_set_query_params(page="home")
    if st.sidebar.button("Daily Transaction Limits Checker"):
        st.experimental_set_query_params(page="Daily_Transaction_Limits_Checker")
    if st.sidebar.button("Daily Transaction Limits Reports"):
        st.experimental_set_query_params(page="Daily_Transaction_Limits_Reports")
    if st.sidebar.button("Transaction Amount Anomaly Detector"):
        st.experimental_set_query_params(page="Transaction_Amount_Anomaly_Detector")
    if st.sidebar.button("Transaction Time Anomaly Detector"):
        st.experimental_set_query_params(page="Transaction_Time_Anomaly_Detector")
    # if st.sidebar.button("Contact"):
    #     st.experimental_set_query_params(page="contact")
    if st.sidebar.button("Actions"):
        st.experimental_set_query_params(page="Actions")
    if st.sidebar.button("Transaction Limits Information"):
        st.experimental_set_query_params(page="Transaction_Limits_Information")

# Function to get the user from the query parameters
def get_user():
    query_params = st.experimental_get_query_params()
    with open("logfile.txt", "a") as f:
        f.write("Query Parameters: {}\n".format(query_params))
    user = query_params.get('user', [''])[0]
    with open("logfile.txt", "a") as f:
        f.write("User: {}\n".format(user))
    return user

# Function to get the case ID from the query parameters
def get_case_id():
    query_params = st.experimental_get_query_params()
    with open("logfile.txt", "a") as f:
        f.write("Query Parameters: {}\n".format(query_params))
    caseID = query_params.get('caseID', [''])[0]
    with open("logfile.txt", "a") as f:
        f.write("Case ID: {}\n".format(caseID))
    return caseID

# Get the user and case ID from the URL
user = get_user()
caseID = get_case_id()

# Display navigation buttons in the sidebar
display_navigation()

# Display the selected page
if st.experimental_get_query_params().get('page', ['home'])[0] == 'home':
    homepage.login(user)
elif st.experimental_get_query_params().get('page', ['home'])[0] == 'Daily_Transaction_Limits_Checker':
    Daily_Transaction_Limits_Checker.main()
elif st.experimental_get_query_params().get('page', ['home'])[0] == 'Daily_Transaction_Limits_Reports':
    Daily_Transaction_Limits_Reports.main()
elif st.experimental_get_query_params().get('page', ['home'])[0] == 'Transaction_Amount_Anomaly_Detector':
    Transaction_Amount_Anomaly_Detector.main()
elif st.experimental_get_query_params().get('page', ['home'])[0] == 'Transaction_Time_Anomaly_Detector':
    Transaction_Time_Anomaly_Detector.main()
# elif st.experimental_get_query_params().get('page', ['home'])[0] == 'contact':
#     contact.app()
elif st.experimental_get_query_params().get('page', ['home'])[0] == 'Actions':
    Actions.main(caseID)
elif st.experimental_get_query_params().get('page', ['home'])[0] == 'Transaction_Limits_Information':
    Transaction_Limits_Information.main()
else:
    st.error("Page not found")

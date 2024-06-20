import streamlit as st
import pymysql
#from pages import main, Daily_Transaction_Limits_Checker, Daily_Transaction_Limits_Reports

# Database connection details
host = 'XXXXXXXXX'  
username = 'XXXX'  
password = 'XXXXX'  
database = 'XXXXXXX'
port = 3306


# Function to get the user from the query parameters
def get_user():
    query_params = st.experimental_get_query_params()
    user = query_params.get('user', [''])[0]
    return user

# Get the user from the URL
user = get_user()

def login(user):
    if 'login_status' not in st.session_state:
        st.session_state.login_status = False

    if st.session_state.login_status:
        if st.button("Logout"):
            st.session_state.login_status = False
        return True

    st.title("Login")
    username_input = st.text_input("Username", value=user)  # Set default value to user
    password_input = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            connection = pymysql.connect(host=host, user=username, password=password, database=database, port=port)
            cursor = connection.cursor()

            query = "SELECT * FROM Portal_Users WHERE username=%s AND password=%s"
            cursor.execute(query, (username_input, password_input))
            user = cursor.fetchone()

            if user:
                st.success("Logged in as {}".format(username_input))
                st.session_state.login_status = True
                return True

            else:
                st.error("Invalid username or password")

            cursor.close()
            connection.close()

        except pymysql.Error as e:
            st.error("Error connecting to the database: {}".format(e))

    return False

if __name__ == "__main__":
    # Function to set the user in the URL query parameters
    def set_user(user):
        st.experimental_set_query_params(user=user)

    if login(user):
        set_user(user)
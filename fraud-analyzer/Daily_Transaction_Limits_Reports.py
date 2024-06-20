import pandas as pd
import mysql.connector
import streamlit as st
from db_config import DB_CONFIG_LOCALHOST
import csv
import io

def check_login():
    if not st.session_state.get("login_status"):
        st.warning("Please log in to access this page.")
        st.stop()  # Stop further execution if not logged in

# Function to retrieve data from MySQL tables
def retrieve_data_from_mysql(start_date, end_date):
    try:
        # Connect to the database
        localhost_connection = mysql.connector.connect(**DB_CONFIG_LOCALHOST)
        cursor = localhost_connection.cursor(dictionary=True)
        
        # Execute queries to retrieve data from the tables
        cursor.execute("SELECT * FROM xxxxxxxxxxxxxxxxxxxxxx WHERE created_at BETWEEN %s AND %s ORDER BY created_at DESC", (start_date, end_date))
        transaction_limits_data = cursor.fetchall()
        
        cursor.execute("SELECT * FROM xxxxxxxxxxxxxxxxxxxxxx WHERE created_at BETWEEN %s AND %s ORDER BY created_at DESC", (start_date, end_date))
        overall_transaction_limits_data = cursor.fetchall()
        
        return transaction_limits_data, overall_transaction_limits_data
    
    except mysql.connector.Error as err:
        st.error(f"Error accessing MySQL: {err}")
        return None, None
        
# Function to format paying_amount column with commas
def daily_format_data(data):
    for row in data:
        row['paying_amount'] = '{:,.2f}'.format(float(row['paying_amount']))  # Convert to float and then format with commas and 2 decimal places
        row['daily_limit'] = '{:,.2f}'.format(float(row['daily_limit']))  # Convert to float and then format with commas and 2 decimal places
    return data

def overall_format_data(data):
    for row in data:
        row['paying_amount'] = '{:,.2f}'.format(float(row['paying_amount']))  # Convert to float and then format with commas and 2 decimal places
        row['overall_daily_limit'] = '{:,.2f}'.format(float(row['overall_daily_limit']))  # Convert to float and then format with commas and 2 decimal places
    return data

# Function to convert data to CSV format
def convert_to_csv(data):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

# Streamlit UI
def main():
    check_login()
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Daily Transaction Limits Report</h1>", unsafe_allow_html=True)
    
    # Date picker
    #selected_date = st.date_input("Select a date")
    # Date range picker
    start_date = st.date_input("Start date", min_value=None, max_value=None)
    end_date = st.date_input("End date", min_value=start_date if start_date is not None else None, max_value=None)
    
    # Retrieve data from MySQL tables
    transaction_limits_data, overall_transaction_limits_data = retrieve_data_from_mysql(start_date, end_date)

    if transaction_limits_data:
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
                df_style = df.style.apply(lambda row: ['background: #d1de6f; color: black']*len(row) if row['staff'] == 'YES' else ['']*len(row), axis=1)
                st.table(df_style)
                # st.table(formatted_data)
                # Download button for transaction limits data
                csv_data = convert_to_csv(formatted_data)
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")
                #button_html = f'<button style="background-color: #008CBA; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Download {fund_transfer_type} Transaction Limits CSV ({start_date_str} to {end_date_str})</button>'
                #st.markdown(button_html, unsafe_allow_html=True)
                st.download_button(label=f"Download {fund_transfer_type} Transaction Limits CSV ({start_date_str}_to_{end_date_str})", data=csv_data, file_name=f"{fund_transfer_type}_transaction_limits_{start_date_str}_to_{end_date_str}.csv", mime="text/csv", key=f"{fund_transfer_type}_download_button")

                # formatted_data = daily_format_data(filtered_data)
                # df = pd.DataFrame(formatted_data)
                # df['staff'] = df['staff'].apply(lambda x: 'YES' if x == 'YES' else '')
                # df_style = df.style.apply(lambda row: {'background-color': 'yellow', 'color': 'black'} if row['staff'] == 'YES' else {}, axis=1)
                # st.table(df_style)
                # csv_data = df_style.to_csv(index=False).encode('utf-8')
                # st.download_button(label=f"Download {fund_transfer_type} Transaction Limits CSV", data=csv_data, file_name=f"{fund_transfer_type}_transaction_limits.csv", mime="text/csv", key=f"{fund_transfer_type}_download_button")

            else:
                st.write(f"No data available for {fund_transfer_type} daily transaction limits.")

    else:
        st.write("No data available for the selected date.")

    if overall_transaction_limits_data:
        overall_formated_data = overall_format_data(overall_transaction_limits_data)
        # st.header("Overall Transaction Limits")
        st.markdown(f"<h1 style='text-align: left; font-size: 25px;'>Overall Transaction Limits</h1>", unsafe_allow_html=True)
        overall_df = pd.DataFrame(overall_formated_data)
        overall_df_style = overall_df.style.apply(lambda row: ['background: #d1de6f; color: black']*len(row) if row['staff'] == 'YES' else ['']*len(row), axis=1)
        st.table(overall_df_style)
        # Download button for overall transaction limits data
        csv_data = convert_to_csv(overall_formated_data)
        #button_html = f'<button style="background-color: #008CBA; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Download Overall Transaction Limits CSV ({start_date_str} to {end_date_str})</button>'
        #st.markdown(button_html, unsafe_allow_html=True)
        st.download_button(label=f"Download Overall Transaction Limits CSV ({start_date_str}_to_{end_date_str})", data=csv_data, file_name=f"overall_transaction_limits_{start_date_str}_to_{end_date_str}.csv", mime="text/csv", key="overall_download_button")
    else:
        # st.header("Overall Transaction Limits")
        st.markdown(f"<h1 style='text-align: left; font-size: 25px;'>Overall Transaction Limits</h1>", unsafe_allow_html=True)
        st.write("No data available for overall transaction limits.")

if __name__ == "__main__":
    main()

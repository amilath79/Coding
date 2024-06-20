import streamlit as st
from datetime import timedelta

def main():
    def display_daily_limits():
        st.markdown("<h1 style='text-align: center; font-size: 30px;'>Daily Transaction Limits</h1>", unsafe_allow_html=True)

        limits = {
            "CF TO CF": "2,500,000.00",
            "CF TO OTHER": "2,500,000.00",
            "OTHER TO OTHER": "250,000.00",
            "OTHER TO CF": "250,000.00",
            "Overall Daily Limit": "3,000,000.00"
        }

        # Create a list of dictionaries for each limit type and value
        limits_data = [{"Limit Type": limit_type, "Limit Value": limit_value} for limit_type, limit_value in limits.items()]

        # Display the information in a table
        st.table(limits_data)

    # Call the function to display daily limits in a table
    display_daily_limits()

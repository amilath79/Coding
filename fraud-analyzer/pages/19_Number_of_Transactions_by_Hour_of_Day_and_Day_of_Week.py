import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import mysql.connector


def check_login():
    if not st.session_state.get("login_status"):
        st.warning("Please log in to access this page.")
        st.stop()  # Stop further execution if not logged in


# Connect to your MySQL database
conn = mysql.connector.connect(
host="cf-live-instance-1.cffbyc0akued.us-east-2.rds.amazonaws.com",
user="analyzerDbUser",
password="7eocmV5ZxQN0",
database="cf_live_app",
charset="utf8mb4",
port=3306)

check_login()

# Your SQL query
query = """
SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
        t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
        t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
        t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
        t1.platform, t1.status
FROM transaction t1
JOIN transaction t2 ON t1.linked_tran_id = t2.id
JOIN app_user t3 ON t3.username = t1.payer_id   
AND t1.created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) -- Up to the past 6 months
AND t1.created_at < CURDATE() - INTERVAL 1 DAY 
WHERE t1.id < t2.id
"""

# Execute the query and load the result into a DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Convert 'created_at' column to datetime format
df['created_at'] = pd.to_datetime(df['created_at'])

# Extract the hour of the day and day of the week
df['hour_of_day'] = df['created_at'].dt.hour
df['day_of_week'] = df['created_at'].dt.day_name()

# Reorder days of the week
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)

# Create a pivot table for the heatmap
heatmap_data = df.pivot_table(index='hour_of_day', columns='day_of_week', aggfunc='size', fill_value=0)

# Streamlit app
st.markdown("<h1 style='text-align: center; font-size: 30px;'>Number of Transactions by Hour of Day and Day of Week</h1>", unsafe_allow_html=True)
st.markdown("This analysis promptly spots peak transaction hours/days/weeks/months. It determines the busiest hours or days for transactions. This can help allocate resources more effectively during high-demand periods in Centrix.")

# Plotting
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt=".0f", linewidths=.5)
plt.title('Number of Transactions by Hour of Day and Day of Week')
plt.xlabel('Day of Week')
plt.ylabel('Hour of Day')

# Save the plot to a BytesIO object
buffer = BytesIO()
plt.savefig(buffer, format='png', bbox_inches='tight')
buffer.seek(0)

# Encode the plot image to base64 for displaying in Streamlit
encoded_image = base64.b64encode(buffer.read()).decode()

# Close the plot
plt.close()

# Display the heatmap
st.image(f'data:image/png;base64,{encoded_image}')

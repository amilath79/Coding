import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import numpy as np
import streamlit as st
import mysql.connector

# Function to load data from MySQL
@st.cache_data
def load_data_from_mysql(query):
    connection = mysql.connector.connect(
    host="xxxxxxxxxxxxxxxxxxxxxx",
    user="xxxxxxxxxxxxxxxxxxxxxx",
    password="xxxxxxxxxxxxxxxxxxxxxx",
    database="xxxxxxxxxxxxxxxxxxxxxx",
    charset="xxxxxxxxxxxxxxxxxxxxxx",
    port=3306)

    data = pd.read_sql(query, connection)
    connection.close()
    return data

# Function for feature engineering
def feature_engineering(data):
    data['hour'] = data['created_at'].dt.hour
    data['day_of_week'] = data['created_at'].dt.dayofweek
    data['amount_log'] = data['paying_amount'].apply(lambda x: 0 if x == 0 else round(np.log(x), 2))
    return data

# Function to train anomaly detection model
def train_anomaly_model(user_profiles, features):
    clf = OneClassSVM(kernel='rbf', nu=0.01)
    scaler = StandardScaler()

    # Impute missing values and standardize user profiles
    user_profiles_imputed = SimpleImputer(strategy='mean').fit_transform(user_profiles[features])
    user_profiles_scaled = scaler.fit_transform(user_profiles_imputed)

    clf.fit(user_profiles_scaled)
    return clf, scaler

# Function to detect anomalies
def detect_anomalies(model, scaler, live_data, features):
    live_data_merged = pd.merge(live_data, user_profiles, on=['nic', 'name'], how='left')
    live_data_merged['hour'] = live_data_merged['created_at'].dt.hour
    live_data_merged['day_of_week'] = live_data_merged['created_at'].dt.dayofweek
    live_data_merged['amount_log'] = live_data_merged['paying_amount'].apply(lambda x: 0 if x == 0 else round(np.log(x), 2))
    
    live_data_merged_imputed = SimpleImputer(strategy='mean').fit_transform(live_data_merged[features])
    live_data_merged_scaled = scaler.transform(live_data_merged_imputed)
    
    decision_function_scores = model.decision_function(live_data_merged_scaled)
    return decision_function_scores

# Function to display anomalies
def display_anomalies(live_data, z_scores, threshold, decision_function_scores, historical_data, user_transaction_count_mean):
    for index, row in live_data.iterrows():
        if z_scores[index] < threshold:
            with st.expander(f"Anomaly Transaction Detected - ID: {row['id']}"):
                st.text(f'''Name: {row['name']}
NIC: {row['nic']}
Paying Amount: {row['paying_amount']}
Time: {row['created_at']}
Mobile No: {row['payer_mobile']}''')

                user_history = historical_data[
                    (historical_data['nic'] == row['nic']) &
                    (historical_data['name'] == row['name'])
                ]

                if not user_history.empty:
                    st.markdown("<h2 style='text-align: Left; font-size: 20px;'>User Transaction History:</h2>", unsafe_allow_html=True)
                    st.dataframe(user_history[['created_at', 'paying_amount', 'payer_bank_name', 'final_payee_bank_name']].astype({'paying_amount': int}).style.set_properties(subset=['paying_amount'], **{'width': '300px'}))
                else:
                    st.write("No historical transactions available for the user.")

                user_daily_count = user_transaction_count_mean[
                    (user_transaction_count_mean['nic'] == row['nic']) &
                    (user_transaction_count_mean['name'] == row['name'])
                ]

                if not user_daily_count.empty:
                    historical_daily_count_mean = user_daily_count['transaction_count_mean'].values[0]
                    actual_daily_count = len(live_data[
                        (live_data['nic'] == row['nic']) &
                        (live_data['name'] == row['name']) &
                        (live_data['created_at'].dt.date == row['created_at'].date())
                    ])

                    st.markdown("<h2 style='text-align: Left; font-size: 20px;'>Conclusion : </h2>", unsafe_allow_html=True)

                    if actual_daily_count > historical_daily_count_mean:
                        st.write(f"Historical Daily Transaction Count Mean: {historical_daily_count_mean}")
                        st.write(f"Actual Daily Count: {actual_daily_count}")
                    else:
                        st.write("Rule Status: Normal Transaction")
                else:
                    st.write("Rule Status: No historical transaction count available for the user on this day.")

                st.write(f"Decision Function Score: {decision_function_scores[index]}")
                st.write(f"Z-Score: {z_scores[index]}")

                if decision_function_scores[index] < 0:
                    st.write("Explanation: This transaction is flagged as an anomaly because it deviates from the user's typical behavior.")
                else:
                    st.write("Explanation: This transaction is considered normal.")

# Streamlit App
st.markdown("<h1 style='text-align: center; font-size: 30px;'>Transaction Behavior Anomaly Detector</h1>", unsafe_allow_html=True)
st.markdown("This facet of the analysis aims to Uncover the behaviour of outlier transactions by analysing the daily and weekly patterns in transactional activity. Simultaneously, it raises alerts, highlighting potential anomalies for immediate attention.")

# Load historical and live data
historical_query = '''
    SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
    t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
    t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
    t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
    t1.platform, t1.status
    FROM xxxxxxxxxxxxxxxxxxxxxx t1
    JOIN xxxxxxxxxxxxxxxxxxxxxx t2 ON t1.linked_tran_id = t2.id
    JOIN xxxxxxxxxxxxxxxxxxxxxx t3 ON t3.username = t1.payer_id   
    AND t1.created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) -- Up to the past 6 months
    AND t1.created_at < CURDATE() - INTERVAL 1 DAY 
    WHERE t1.id < t2.id
'''
historical_data = load_data_from_mysql(historical_query)
historical_data = feature_engineering(historical_data)

live_query = '''
    SELECT t1.id, t3.name, t3.nic, t1.created_at, t1.device_id, t1.device_model, 
    t1.final_payee_account_number, t1.final_payee_bank_name, t1.fund_transfer_type, 
    t1.payer_account_number, t1.payer_bank_name, t1.payer_email, t1.payer_id, t1.payer_mobile, 
    t1.paying_amount, t1.payment_category, t1.payment_description, t1.payment_processor, 
    t1.platform, t1.status
    FROM xxxxxxxxxxxxxxxxxxxxxx t1
    JOIN xxxxxxxxxxxxxxxxxxxxxx t2 ON t1.linked_tran_id = t2.id
    JOIN xxxxxxxxxxxxxxxxxxxxxx t3 ON t3.username = t1.payer_id   
    AND t1.created_at >= CONCAT(CURDATE(), ' 00:00:00');
    WHERE t1.id < t2.id
'''
live_data = load_data_from_mysql(live_query)
live_data = feature_engineering(live_data)

# Create user profiles
user_profiles = historical_data.groupby(['nic', 'name']).agg({
    'hour': 'mean',
    'day_of_week': 'mean',
    'amount_log': 'mean'
}).reset_index()

user_transaction_count_mean = historical_data.groupby(['nic', 'name']).size().reset_index(name='transaction_count_mean')

# Train anomaly detection model
model, scaler = train_anomaly_model(user_profiles, ['hour', 'day_of_week', 'amount_log'])

# Detect anomalies
decision_function_scores = detect_anomalies(model, scaler, live_data, ['hour', 'day_of_week', 'amount_log'])

# Calculate Z-scores
mean_score = np.mean(decision_function_scores)
std_dev_score = np.std(decision_function_scores)
z_scores = (decision_function_scores - mean_score) / std_dev_score

# Streamlit App
st.markdown("<h1 style='text-align: center; font-size: 30px;'>Transaction Behavior Anomaly Detector</h1>", unsafe_allow_html=True)
st.markdown("This facet of the analysis aims to Uncover the behaviour of outlier transactions by analysing the daily and weekly patterns in transactional activity. Simultaneously, it raises alerts, highlighting potential anomalies for immediate attention.")

# Add a slider for Z-score threshold adjustment
threshold = st.slider('Z-score threshold', min_value=-1.0, max_value=1.0, value=-0.60, step=0.1)

# Display anomalies
display_anomalies(live_data, z_scores, threshold, decision_function_scores, historical_data, user_transaction_count_mean)

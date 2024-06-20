import pandas as pd
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import mysql.connector

# # Load your Excel file into a DataFrame from the given URL
# path = "https://github.com/damika9996/Word-Cloud/raw/b2a9e910c8e2d0bf2d077fa3edc8ee4d17905556/NewDFWORD.xlsx"
# df = pd.read_excel(path)

def check_login():
    if not st.session_state.get("login_status"):
        st.warning("Please log in to access this page.")
        st.stop()  # Stop further execution if not logged in

# Connect to your MySQL database
conn = mysql.connector.connect(
host="xxxxxxxxxxxxxxxxxxxxxx",
user="xxxxxxxxxxxxxxxxxxxxxx",
password="xxxxxxxxxxxxxxxxxxxxxx",
database="xxxxxxxxxxxxxxxxxxxxxx",
charset="xxxxxxxxxxxxxxxxxxxxxx",
port=3306)

check_login()

# Your SQL query
query = """
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
"""

# Execute the query and load the result into a DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Assuming your column is named 'payment_description'
text = ' '.join(df['payment_description'].astype(str))

# Function to generate the word cloud
def generate_wordcloud():
    fig, ax = plt.subplots(figsize=(10, 7))
    wordcloud = WordCloud(width=800, height=400, random_state=21, max_font_size=110, background_color='white').generate(text)
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis('off')
    st.pyplot(fig)

# Function to update the count when the button is clicked
def update_count():
    if 'selected_word' not in st.session_state:
        st.session_state.selected_word = ''  # Initialize selected_word to an empty string if not present

    selected_word = st.session_state.selected_word
    if selected_word:
        selected_count = df[df['payment_description'].str.lower() == selected_word.lower()].shape[0]
        st.write(f"The word '{selected_word}' appears {selected_count} times.")
    else:
        st.warning("Please select a word.")

st.markdown("<h1 style='text-align: center; font-size: 30px;'>Payment Description Word Cloud</h1>", unsafe_allow_html=True)
st.markdown("The word cloud visually represents the frequency of words in the 'payment_description' of the data frame. The overall purpose is to provide a user interface based on user description (comment) when selecting or searching a word and get count.")

# Combobox with search bar
selected_word = st.selectbox('Search Word:', ['Select a word'] + list(df['payment_description'].unique()))

# Button to trigger the count update
if st.button("Get Count"):
    st.session_state.selected_word = selected_word
    update_count()

# Show the initial word cloud
generate_wordcloud()

# Initial display of count
update_count()

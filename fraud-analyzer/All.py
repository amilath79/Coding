import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load data from the provided CSV file
data_url = 'https://xxxxxxxxxxxxxxxxxxxxxx.csv'
df = pd.read_csv(data_url)

# Convert 'created_at' column to datetime format if not already
df['created_at'] = pd.to_datetime(df['created_at'])

# Extract year-month and set it as a new column
df['year_month'] = df['created_at'].dt.to_period('M')

# Filter data for September 2023
september_data = df[df['year_month'] == '2023-09']

# Group by date and calculate the daily transaction count
daily_transaction_count = september_data.groupby(september_data['created_at'].dt.date).size().reset_index(name='transaction_count')

# Get the top 10 payers and top 10 payees
top_payers = df['payer_bank_name'].value_counts().nlargest(10).index
top_payees = df['final_payee_bank_name'].value_counts().nlargest(10).index

# Filter the DataFrame based on the top payers and payees
filtered_df = df[df['payer_bank_name'].isin(top_payers) & df['final_payee_bank_name'].isin(top_payees)]

# Set up the Streamlit app
st.title('Centrix Data Analysis')

# Use markdown headers as "tabs"
tabs = ["# Daily Transaction Count",
        "# Interactive Heatmap",
        "# Yearly Average Pie Chart",
        "# Distribution of Transactions",
        "# Transaction Volume Over Time"]

selected_tab = st.sidebar.radio("Select Analysis", tabs)

if selected_tab == tabs[0]:
    st.header('Daily Transaction Count in September 2023')
    st.line_chart(daily_transaction_count.set_index('created_at'))

elif selected_tab == tabs[1]:
    st.header('Interactive Bank-to-Bank Transactions Heatmap')
    selected_value = st.radio('Select Metric:', ['transaction_count', 'total_amount'], index=0)

    # Group by payer_bank_name, final_payee_bank_name, and calculate count and total amount
    grouped_df = filtered_df.groupby(['payer_bank_name', 'final_payee_bank_name']).agg(
        transaction_count=pd.NamedAgg(column='paying_amount', aggfunc='count'),
        total_amount=pd.NamedAgg(column='paying_amount', aggfunc='sum')
    ).reset_index()

    # Pivot the DataFrame to create a matrix of payer banks vs. final payee banks
    pivot_df = grouped_df.pivot(index='payer_bank_name', columns='final_payee_bank_name', values=selected_value).fillna(0)

    # Divide the values by 1000 for 'total_amount' and format the annotations accordingly
    if selected_value == 'total_amount':
        pivot_df = pivot_df / 1000

    # Sort the index (Y-axis) in descending order
    pivot_df = pivot_df.sort_index(ascending=False)

    # Display the heatmap using Seaborn
    plt.figure(figsize=(18, 12))
    sns.heatmap(pivot_df, cmap='YlGnBu', annot=True, fmt='.1f' if selected_value == 'total_amount' else '.0f',
                cbar_kws={'label': selected_value}, linewidths=0.5, square=True, annot_kws={'size': 8})
    st.pyplot()

elif selected_tab == tabs[2]:
    st.header('Yearly Average Transaction Count by Payment Category')
    avg_df = df.groupby(['payment_category', df['created_at'].dt.year])['id'].count().reset_index()

    fig = px.pie(
        avg_df,
        names='payment_category',
        values='id',
        title='Yearly Average Transaction Count by Payment Category',
        labels={'payment_category': 'Payment Category', 'id': 'Transaction Count'},
        color='payment_category',
        color_discrete_map=px.colors.sequential.Viridis,
    )
    st.plotly_chart(fig)

elif selected_tab == tabs[3]:
    st.header('Distribution of Transactions by Fund Transfer Type')
    pie_data = df['fund_transfer_type'].value_counts().reset_index()
    pie_data.columns = ['fund_transfer_type', 'transaction_count']

    fig = px.pie(
        pie_data,
        names='fund_transfer_type',
        values='transaction_count',
        title='Distribution of Transactions by Fund Transfer Type',
        labels={'fund_transfer_type': 'Fund Transfer Type', 'transaction_count': 'Transaction Count'},
        color='fund_transfer_type',
        color_discrete_map=px.colors.sequential.Viridis,
    )
    st.plotly_chart(fig)

elif selected_tab == tabs[4]:
    st.header('Transaction Volume Over Time')
    line_data = df.groupby(df['created_at'].dt.date).size().reset_index(name='transaction_count')

    fig = px.line(
        line_data,
        x='created_at',
        y='transaction_count',
        title='Transaction Volume Over Time',
        labels={'created_at': 'Date', 'transaction_count': 'Transaction Count'},
    )
    st.plotly_chart(fig)

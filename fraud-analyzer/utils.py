import streamlit as st

def get_case_id():
    query_params = st.experimental_get_query_params()
    
    # Log query parameters to a file for debugging
    with open("logfile1.txt", "a") as f:
        f.write("Query Parameters: {}\n".format(query_params))
    
    case_id = query_params.get('case_id', [''])[0]
    
    # Log the retrieved case_id for debugging
    with open("logfile.txt", "a") as f:
        f.write("Case ID: {}\n".format(case_id))
    
    return case_id

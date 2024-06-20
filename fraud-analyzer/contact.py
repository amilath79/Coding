import streamlit as st
from urllib.parse import urlencode, urlparse, parse_qs

def app():
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
    else:
        escalate_options = ['Digital Manager', 'Head of Digital & Fintech', 'Compliance']

    # Create the second dropdown menu
    escalate_selected_option = st.selectbox('Case Escalate to:', escalate_options, index=escalate_options.index(escalate_selected_option) if escalate_selected_option in escalate_options else 0, disabled=True)

    # Update the query parameters in the URL
    new_params = {"page": "contact", "selected_option": selected_option}
    st.experimental_set_query_params(**new_params)

    # Display messages based on the selections
    if escalate_selected_option == 'Head of Digital & Fintech':
        message = 'Escalated to head_of_Digital_&_fintech'
        st.write(message)
    elif escalate_selected_option == 'Compliance':
        message = 'Escalated to Compliance'
        st.write(message)

    # # Generate and display a shareable link
    # base_url = urlparse(st.experimental_get_query_params())
    # query_string = urlencode(new_params)
    # shareable_url = f"{base_url.scheme}://{base_url.netloc}{base_url.path}?{query_string}"

    # st.write(f"Shareable link: [Click here]({shareable_url})")

if __name__ == "__main__":
    app()

import streamlit as st
import about
import Home
from . import contact
from pages import home

# Create a dictionary mapping page names to module functions
pages = {
    "Home": Home,
    "About": about,
    "Contact": contact
}

# Add a radio button for navigation in the sidebar
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

# Call the app function corresponding to the selected page
page = pages[selection]
page.app()

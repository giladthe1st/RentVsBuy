import streamlit as st
import rent_vs_buy, investment_property

# Hide the sidebar and menu
st.set_page_config(layout="wide")

# Initialize session state for page selection if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Rent vs. Buy"

# Create two columns for the buttons
col1, col2 = st.columns(2)

# Create buttons for navigation
with col1:
    if st.button("Rent vs. Buy", use_container_width=True):
        st.session_state.current_page = "Rent vs. Buy"
with col2:
    if st.button("Investment Property", use_container_width=True):
        st.session_state.current_page = "Investment Property"

# Display the selected page
if st.session_state.current_page == "Rent vs. Buy":
    rent_vs_buy.show()
else:
    investment_property.show()

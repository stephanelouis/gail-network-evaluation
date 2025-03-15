"""
= = = = = = = = = = = =
AI Case Studies Evaluation Hub
= = = = = = = = = = = =

This module manages the Evaluation Hub web application, which serves the following purposes:
- **Dashboard**: Analytics and metrics for case studies
- **Evaluation Inputs**: Interface for reviewing and rating case studies
- **Evaluation Summary**: Overview of evaluation results

Author:        Stéphane Bouvier
Created On:    2025-03-14
Last Updated:  2025-03-14
Version:       1.0.0
"""

import streamlit as st
import re
import json
import os

# Set up Streamlit page layout & title first, before any other st commands
st.set_page_config(
    page_title="Case Study Evaluation Hub", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Then import modules that might use streamlit
from tabs import tab1_dashboard, tab2_evaluation_inputs, tab3_evaluation_summary

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'email' not in st.session_state:
    st.session_state.email = ""

def get_authorized_emails():
    """Get authorized emails from local file or Streamlit secrets"""
   
    # Try local file first
    local_auth_path = "config/authorized_emails.json"
    if os.path.exists(local_auth_path):
        try:
            with open(local_auth_path, 'r') as f:
                data = json.load(f)
                return data.get('authorized_emails', [])
        except Exception as e:
            st.error(f"Error reading local auth file: {str(e)}")
            return []
    
    # Fall back to Streamlit secrets
    if st.secrets and "AUTHORIZED_EMAILS" in st.secrets:
        try:
            if isinstance(st.secrets["AUTHORIZED_EMAILS"], str):
                return json.loads(st.secrets["AUTHORIZED_EMAILS"])
            return st.secrets["AUTHORIZED_EMAILS"]
        except Exception as e:
            st.error(f"Error reading Streamlit secrets: {str(e)}")
            return []
    
    return []

def is_valid_email(email: str) -> bool:
    """Check if the email format is valid"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_authorized(email: str) -> bool:
    """Check if the email is authorized"""
    authorized_emails = get_authorized_emails()
    return email.lower() in [e.lower() for e in authorized_emails]

# Authentication UI
if not st.session_state.authenticated:
    
    st.title("Welcome to AI Case Study Evaluation Hub")
    st.markdown("Please enter your email to access the application.")
    
    # Create a form for email input
    with st.form("auth_form"):
        email = st.text_input("Email Address").strip()
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not email:
                st.error("Please enter your email address.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            elif not is_authorized(email):
                st.error("You do not have access to this application. Please contact the administrator.")
            else:
                st.session_state.authenticated = True
                st.session_state.email = email
                st.rerun()

# Main application UI (only shown to authenticated users)
if st.session_state.authenticated:
    # Add a welcome message and logout button in the sidebar
    with st.sidebar:
        st.write(f"Welcome, {st.session_state.email}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.email = ""
            st.rerun()
    
    # Add a title above the tabs
    st.title("AI Case Study Evaluation Hub")

    # Define tabs for different functionalities
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard", 
        "📝 Evaluation Inputs", 
        "📈 Evaluation Summary"
    ])

    # = = = = = = = = = = = = = = = = = = = =
    # TAB 1: DASHBOARD
    # = = = = = = = = = = = = = = = = = = = =
    with tab1:
        tab1_dashboard.display_tab()

    # = = = = = = = = = = = = = = = = = = = =
    # TAB 2: EVALUATION
    # = = = = = = = = = = = = = = = = = = = =
    with tab2:
        tab2_evaluation_inputs.display_tab()

    # = = = = = = = = = = = = = = = = = = = =
    # TAB 3: SUMMARY
    # = = = = = = = = = = = = = = = = = = = =
    with tab3:
        tab3_evaluation_summary.display_tab() 
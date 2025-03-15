"""
Authentication module for the Case Study Evaluation Hub.
Handles user authentication and authorization.
"""

import streamlit as st
import re
import json
import os

def init_auth_state():
    """Initialize authentication state"""
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

def show_login_page():
    """Display the login page"""

    st.title("Welcome to AI Case Study Evaluation Hub")
    st.markdown("Please enter your email to access the application.")
    
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

def check_authentication():
    """Check if user is authenticated and show appropriate page"""
    
    init_auth_state()
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    return True 
"""
= = = = = = = = = = = =
AI Case Studies Evaluation Hub
= = = = = = = = = = = =

This module manages the Evaluation Hub web application, which serves the following purposes:
- **Dashboard**: Analytics and metrics for case studies
- **Evaluation Inputs**: Interface for reviewing and rating case studies
- **Evaluation Summary**: Overview of evaluation results
"""

import streamlit as st

# Set up Streamlit page layout & title first, before any other st commands
st.set_page_config(
    page_title="Case Study Evaluation Hub", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar
)

# Then import modules that might use streamlit
from tabs import tab1_dashboard, tab2_case_study_evaluation, tab3_evaluation_summary
from utils.auth import check_authentication

# Check authentication and show appropriate content
authenticated = check_authentication()

if authenticated:
    # Add a title and user info at the top
    st.title("AI Case Study Evaluation Hub")
    st.markdown(f"*Logged in as: {st.session_state.email}*")
    st.markdown("---")  # Add a separator line

    # Define tabs for different functionalities
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard", 
        "📝 Case Study Evaluation", 
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
        tab2_case_study_evaluation.display_tab()

    # = = = = = = = = = = = = = = = = = = = =
    # TAB 3: SUMMARY
    # = = = = = = = = = = = = = = = = = = = =
    with tab3:
        tab3_evaluation_summary.display_tab() 
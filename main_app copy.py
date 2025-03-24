"""
= = = = = = = = = = = =
AI Case Studies Evaluation Hub
= = = = = = = = = = = =

This webapp manages the Evaluation Hub web application, which serves the following purposes:

- **Guidelines**: Analytics and metrics for case studies
- **Evaluation Inputs**: Interface for reviewing and rating case studies
- **Evaluation Summary**: Overview of evaluation results
"""

import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Streamlit page layout & title first, before any other st commands
st.set_page_config(
    page_title="Case Study Evaluation Hub", 
    layout="wide"
)

# Then import modules that might use streamlit
from tabs import tab1_guidelines, tab2_evaluation, tab3_user_summary, tab4_team_summary
from utils.auth import check_authentication
from utils.firestore_manager import get_user_evaluations_count

# Check authentication and show appropriate content
authenticated = check_authentication()

if authenticated:
    
    # Add a title and user info at the top
    st.title("AI Case Study Evaluation Hub")
    st.markdown(f"*Logged in as: {st.session_state.email}*")
    
    # Color-coded review count
    review_count = get_user_evaluations_count(st.session_state.email)
    if review_count == 0:
        st.markdown(f"*Case studies reviewed*: {review_count} / 10")
    elif review_count < 10:
        st.markdown(f"*Case studies reviewed*: {review_count} / 10")
    else:
        st.markdown(f"*Case studies reviewed: {review_count}*")

    # Initialize current tab in session state if not exists
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Guidelines"

    # Define tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Guidelines", 
        "📝 Evaluation", 
        "📈 User Summary",
        "📈 Team Summary"
    ])

    # Function to handle tab change
    def handle_tab_change(tab_name):
        if st.session_state.current_tab != tab_name:
            st.session_state.current_tab = tab_name
            logger.info(f"Tab changed to: {tab_name}")

    # = = = = = = = = = = = = = = = = = = = =
    # TAB 1: GUIDELINES
    # = = = = = = = = = = = = = = = = = = = =
    with tab1:
        handle_tab_change("Guidelines")
        tab1_guidelines.display_content()

    # = = = = = = = = = = = = = = = = = = = =
    # TAB 2: EVALUATION
    # = = = = = = = = = = = = = = = = = = = =
    with tab2:
        handle_tab_change("Evaluation")
        tab2_evaluation.display_content()

    # = = = = = = = = = = = = = = = = = = = =
    # TAB 3: USER SUMMARY
    # = = = = = = = = = = = = = = = = = = = =
    with tab3:
        handle_tab_change("User Summary")
        tab3_user_summary.display_content()
        
    # = = = = = = = = = = = = = = = = = = = =
    # TAB 4: TEAM SUMMARY
    # = = = = = = = = = = = = = = = = = = = =
    with tab4:
        handle_tab_change("Team Summary")
        tab4_team_summary.display_content()
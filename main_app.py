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

from utils.auth import check_authentication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Streamlit page layout & title first, before any other st commands
st.set_page_config(
    page_title="Case Study Evaluation Hub", 
    layout="wide"
)

# Check authentication and show appropriate content
authenticated = check_authentication()

# TODO: Add a page to display the current version of the app
if authenticated:

    pg = st.navigation([
        st.Page("_1_Dashboard.py"), 
        st.Page("_2_Case_Study_Evaluation (1).py"), 
        st.Page("_3_Case_Study_Evaluation (2).py"), 
        st.Page("_4_Writing_Comparison.py"), 
        st.Page("_5_Multi_Sources_Addition.py"), 
        st.Page("_99_Case_Studies_Library.py"), 
        ])
    pg.run()
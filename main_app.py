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

# Set up Streamlit page layout & title first, before any other st commands
st.set_page_config(
    page_title="Case Study Evaluation Hub", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Then import modules that might use streamlit
from tabs import tab1_dashboard, tab2_evaluation_inputs, tab3_evaluation_summary

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
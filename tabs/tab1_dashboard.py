"""
Dashboard Tab for the Case Study Evaluation Hub.
Displays analytics and metrics for case studies.
"""

import streamlit as st

def display_tab():
    st.header("Analytics Dashboard")
    st.info("Dashboard will show analytics and metrics for case studies, including:\n" +
            "- Total number of case studies\n" +
            "- Distribution by industry\n" +
            "- Distribution by business function\n" +
            "- Distribution by business impact") 
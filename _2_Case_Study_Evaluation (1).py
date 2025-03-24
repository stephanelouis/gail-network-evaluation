import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from modules._2_case_study_evaluation_1.main import display_content_page

# Display the dashboard
display_content_page()

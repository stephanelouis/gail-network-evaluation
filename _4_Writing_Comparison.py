import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from modules._4_writing_comparison.main import display_content_page

# Display the dashboard
display_content_page()

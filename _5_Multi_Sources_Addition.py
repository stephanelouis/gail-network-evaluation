import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from modules._5_multi_sources_addition.main import display_content_page

# Display the dashboard
display_content_page()

"""Helper functions for URL operations."""

import os
import streamlit as st

def load_company_urls():
    """
    Load company URLs from the config file.
    
    Returns:
        list: Sorted list of unique company URLs.
    """
    try:
        urls_file = "config/company_urls.txt"
        if not os.path.exists(urls_file):
            st.error(f"URLs file not found at {urls_file}")
            return []
            
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        return sorted(list(set(urls)))  # Remove duplicates and sort
    except Exception as e:
        st.error(f"Error loading company URLs: {str(e)}")
        return [] 
import streamlit as st
import pandas as pd

from modules._4_writing_comparison.utils import format_case_study_summary
from utils.firestore_manager import get_one_case_study_per_company
from utils.url_helper import URLHelper

def display_content_page():
    
    # Title and description
    st.title("Writing Comparison Tool")
    st.markdown("""
    This tool allows you to better assess the changes made in the following 2 critical areas:
    - Case studies sound too technical.
    - Case studies sound too vendor-like.
    """)

    try:
        
        # Get one case study per company
        case_studies = get_one_case_study_per_company()
        
        if case_studies:
            st.subheader("Sample Case Studies by Company")
            
            # Display each case study in an expander
            for case in case_studies:
                source_url = case.get('source_url', 'No URL available')
                clean_url = URLHelper.clean_url(source_url)
                
                with st.expander(f"🏢 {clean_url}"):
                    # Create two columns for side-by-side comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Original Summary")
                        # Format old summary
                        old_summary = case.get('case_study_summary_old')
                        formatted_old = format_case_study_summary(old_summary)
                        if formatted_old:
                            st.markdown(formatted_old)
                        else:
                            st.info("No original summary available")
                    
                    with col2:
                        st.markdown("### New Summary")
                        # Format new summary
                        new_summary = case.get('case_study_summary')
                        formatted_new = format_case_study_summary(new_summary)
                        if formatted_new:
                            st.markdown(formatted_new)
                        else:
                            st.info("No new summary available")
                    
                    # Add metadata below the comparison
                    st.markdown("---")
                    st.markdown(f"*Last updated: {case.get('updated_at', 'N/A')}*")
                    st.markdown(f"[Visit Company Website]({clean_url})")
                    
        else:
            st.info("No case studies available")
            
    except Exception as e:
        st.error(f"Error loading case studies: {str(e)}")
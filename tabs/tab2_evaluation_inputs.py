"""
Evaluation Tab for the Case Study Evaluation Hub.
Handles case study review and rating.
"""

import streamlit as st
from webapps.web_backend.utils.firestore_manager import get_random_case_study

def display_tab():

    st.header("Case Study Evaluation")

    # Add a button to fetch a case study
    if st.button("Get Case Study"):

        # Fetch a case study
        case_study = get_random_case_study()
        
        if case_study:

            # Store the case study in session state
            st.session_state['current_case_study'] = case_study
            
            # Display basic case study information
            st.subheader(f"Case Study ID: {case_study.get('id', 'N/A')}")
            st.write(f"Source URL: {case_study.get('source_url', 'N/A')}")
            
            # Display the case study content
            if 'case_study_final' in case_study:
                st.markdown(case_study['case_study_final'])
            else:
                st.warning("No content available for this case study")
        
        else:
            st.error("No case studies found in the database")
    
    # Display current case study if it exists in session state
    elif 'current_case_study' in st.session_state:
        
        case_study = st.session_state['current_case_study']
        st.subheader(f"Case Study ID: {case_study.get('id', 'N/A')}")
        st.write(f"Source URL: {case_study.get('source_url', 'N/A')}")
        
        if 'case_study_final' in case_study:
            st.markdown(case_study['case_study_final'])
        else:
            st.warning("No content available for this case study") 
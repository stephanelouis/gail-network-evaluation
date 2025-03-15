"""
Evaluation Tab for the Case Study Evaluation Hub.
Handles case study review and rating.
"""

import streamlit as st
from utils.firestore_manager import get_random_case_study

def display_evaluation_form(case_study):
    """Display the evaluation form for the case study"""
    
    with st.form("evaluation_form"):

        st.subheader("Evaluation Form")
        
        # Basic Information
        st.write(f"**Case Study ID:** {case_study.get('id', 'N/A')}")
        st.write(f"**Source URL:** {case_study.get('source_url', 'N/A')}")
        
        # Evaluation Criteria
        st.markdown("### Quality Assessment")
        quality_score = st.slider("Overall Quality", 1, 5, 3, help="Rate the overall quality of the case study")
        
        st.markdown("### Implementation Details")
        implementation_clarity = st.select_slider(
            "Implementation Clarity",
            options=["Very Poor", "Poor", "Average", "Good", "Excellent"],
            value="Average",
            help="How clearly are the implementation details explained?"
        )
        
        st.markdown("### Business Impact")
        impact_areas = st.multiselect(
            "Impact Areas",
            ["Cost Reduction", "Revenue Growth", "Process Efficiency", "Customer Experience", "Innovation", "Other"],
            help="Select all areas where this implementation had significant impact"
        )
        
        st.markdown("### Technical Assessment")
        tech_complexity = st.select_slider(
            "Technical Complexity",
            options=["Basic", "Moderate", "Complex", "Very Complex", "Cutting Edge"],
            value="Moderate",
            help="Assess the technical complexity of the implementation"
        )
        
        # Detailed Comments
        st.markdown("### Comments")
        strengths = st.text_area("Strengths", help="What are the main strengths of this case study?")
        weaknesses = st.text_area("Areas for Improvement", help="What aspects could be improved or clarified?")
        notes = st.text_area("Additional Notes", help="Any other observations or comments?")
        
        # Submit button
        submitted = st.form_submit_button("Submit Evaluation")
        if submitted:
            
            # TODO: Save evaluation to database
            st.success("Evaluation submitted successfully!")
            # Clear the current case study to get a new one
            if 'current_case_study' in st.session_state:
                del st.session_state['current_case_study']
            st.rerun()

def display_case_study(case_study):
    """Display the case study content"""
    st.subheader("Case Study Content")
    
    if 'case_study_final' in case_study:
        st.markdown(case_study['case_study_final'])
    else:
        st.warning("No content available for this case study")

def display_tab():
    """Main function to display the evaluation tab"""
    
    st.header("Case Study Evaluation")

    # Add a button to fetch a case study
    if 'current_case_study' not in st.session_state:
        if st.button("Get Random Case Study"):
            case_study = get_random_case_study()
            if case_study:
                st.session_state['current_case_study'] = case_study
                st.rerun()
            else:
                st.error("No case studies found in the database")
    
    # Display current case study if it exists
    if 'current_case_study' in st.session_state:
                
        # Create two columns for the layout
        col1, col2 = st.columns([6, 4])  # 60% for case study, 40% for evaluation
        
        # Left column: Case Study Content
        with col1:
            display_case_study(st.session_state['current_case_study'])
        
        # Right column: Evaluation Form
        with col2:
            display_evaluation_form(st.session_state['current_case_study'])
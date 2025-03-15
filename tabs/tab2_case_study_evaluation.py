"""
Evaluation Tab for the Case Study Evaluation Hub.
Handles case study review and rating.
"""

import streamlit as st
from utils.firestore_manager import get_random_case_study

def display_evaluation_form(case_study):
    """Display the evaluation form for the case study"""
    
    # Initialize session state for selected area if not exists
    if 'selected_area' not in st.session_state:
        st.session_state.selected_area = "Accuracy"  # Default to first option
    
    with st.form("evaluation_form"):
        st.subheader("Evaluation Form")
        
        # Basic Information
        st.write(f"**Case Study ID:** {case_study.get('id', 'N/A')}")
        st.write(f"**Source URL:** {case_study.get('source_url', 'N/A')}")
        
        # 1. Overall Assessment
        st.markdown("##### 1. Overall Assessment")
        confidence_score = st.slider(
            "How likely would you be to recommend publishing this AI-generated case study on the GAiL Network website?",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = Would not recommend at all, 5-6 = Neutral, 7-8 = Would recommend with changes, 9-10 = Would strongly recommend"
        )
        
        # 2. Top Improvement Area
        st.markdown("##### 2. Top Improvement Area")
        
        # Define improvement areas with descriptions
        improvement_areas = {
            "Relevance": "Relevance (Alignment with AI case study goals)",
            "Accuracy": "Accuracy (Factual correctness and data reliability)",
            "Structure": "Structure (Logical organization and clear flow of information)",
            "Depth": "Depth (Appropriate technical detail and thoroughness)",
            "Style": "Style (Clear, professional, and engaging writing)",
            "Tone": "Tone (Appropriate voice and perspective for audience)",
            "Other": "Other (Please specify clearly in your comment)"
        }
        
        # Create radio buttons with descriptions
        st.write("Which of the following areas would you prioritize to immediately improve the output?")
        
        # Use radio buttons with values instead of keys
        selected_area = st.radio(
            "Select one area:",
            options=[improvement_areas[key] for key in improvement_areas.keys()],
            label_visibility="collapsed"
        )
        
        # If "Other" is selected, show text input
        other_area = None
        if "Other" in selected_area:
            other_area = st.text_input("Please specify the other improvement area:")
        
        # 3. Specific Improvement Feedback
        st.markdown("##### 3. Specific Improvement Feedback")
        improvement_feedback = st.text_area(
            "What specifically would you do differently in this area?",
            help="Provide detailed suggestions for improving the selected area"
        )
        
        # Submit button at the bottom of the form
        submitted = st.form_submit_button("Submit Evaluation", type="primary", use_container_width=True)
        
    # Handle form submission outside the form
    if submitted:
        if not improvement_feedback:
            st.error("Please provide specific improvement feedback before submitting.")
            return
        
        # Update session state with form data
        st.session_state.selected_area = selected_area
        
        # Prepare evaluation data
        evaluation_data = {
            "case_study_id": case_study.get('id'),
            "confidence_score": confidence_score,
            "improvement_area": other_area if "Other" in selected_area else selected_area.split(" (")[0],
            "improvement_feedback": improvement_feedback
        }
        
        # TODO: Save evaluation to database
        st.success("Evaluation submitted successfully!")
        
        # Clear the current case study to get a new one
        if 'current_case_study' in st.session_state:
            del st.session_state['current_case_study']
            del st.session_state.selected_area  # Reset selected area
        st.rerun()

def display_case_study(case_study):
    """Display the case study content"""
    
    if 'case_study_final' in case_study:

        st.subheader("Case Study Content")

        # Clean up the content by replacing separator lines with blank lines
        content = case_study['case_study_final']
        content = content.replace("- - - - - - - - -", "\n")
        st.markdown(content)
    
    else:
        st.warning("No content available for this case study")

def display_tab():
    """Main function to display the evaluation tab"""
    
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
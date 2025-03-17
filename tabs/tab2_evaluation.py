"""
Evaluation Tab for the Case Study Evaluation Hub.
Handles case study review and rating.
"""

import streamlit as st
from datetime import datetime
import logging
import uuid
from utils.firestore_manager import get_random_case_study
from utils.firestore_manager import save_evaluation

# Configure logging
logger = logging.getLogger(__name__)

def generate_evaluation_id(case_study_id, user_email):
    """Generate a deterministic UUID from case study ID and user email"""

    # Combine strings and encode to bytes
    combined = f"{case_study_id}:{user_email}".encode('utf-8')

    # Generate UUID version 5 (deterministic) using DNS namespace
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, combined.decode('utf-8')))

# # # # # # # # # # #
# Case Study Content
# # # # # # # # # # #
def display_case_study(case_study):
    """Display the case study content"""
    
    if case_study is None:
        logger.warning("Attempted to display None case study")
        return
        
    if 'case_study_final' in case_study:
        
        logger.info(f"Displaying case study: {case_study.get('id', 'N/A')}")
        st.subheader("Case Study Content")
        st.info("Step 1. Read the case study content carefully.")

        # Clean up the content by replacing separator lines with blank lines
        content = case_study['case_study_final']
        content = content.replace("- - - - - - - - -", "\n")
        st.markdown(content)
    
    else:
        
        logger.warning(f"No content available for case study: {case_study.get('id', 'N/A')}")
        st.warning("No content available for this case study")

# # # # # # # # # # #
# Evaluation Form
# # # # # # # # # # #
def display_evaluation_form(case_study):
    """Display the evaluation form for the case study"""
        
    with st.form("evaluation_form"):

        st.subheader("Evaluation Form")
        st.info("Step 2. Evaluate the case study based on the following criteria.")
        
        # Basic Information
        st.write(f"**Case Study ID:** {case_study.get('id', 'N/A')}")
        st.write(f"**Source URL:** {case_study.get('source_url', 'N/A')}")
        
        # 1. Overall Assessment
        st.markdown("##### 1. Overall Scoring")
        evaluation_score = st.slider(
            "How likely would you be to recommend publishing this AI-generated case study on the GAiL Network website?",
            min_value=1,
            max_value=10,
            value=1,
            help="1 = Would not recommend at all, 5-6 = Neutral, 7-8 = Would recommend with changes, 9-10 = Would strongly recommend"
        )
        
        # 2. Top Improvement Area
        st.markdown("##### 2. Improvement Area")
        
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
        st.write("Which area needs the most improvement?")
        
        # Use radio buttons with values instead of keys
        improvement_area = st.radio(
            "Select one area:",
            options=[improvement_areas[key] for key in improvement_areas.keys()],
            label_visibility="collapsed"
        )
                        
        # 3. Specific Improvement Feedback
        st.markdown("##### 3. Improvement Feedback")
        improvement_feedback = st.text_area(
            "What specifically would you do differently in this area?",
            key="current_feedback",
            help="Provide detailed suggestions for improving the selected area"
        )
        
        # Submit button at the bottom of the form
        if st.form_submit_button("Submit Evaluation", type="primary", use_container_width=True):

            # Error handling
            if not improvement_feedback:
                logger.error("Failed to provide feedback for the improvement area.")
                st.error("Please provide feedback for the improvement area.")
                st.stop()
            
            # Generate evaluation ID from case study ID and user email
            evaluation_id = generate_evaluation_id(
                case_study.get('id'),
                st.session_state.email
            )
            
            # Set firestore object to save
            evaluation_object = {
                "id": evaluation_id,  # Add the generated ID
                "case_study_id": case_study.get('id'),
                "evaluator_email": st.session_state.email,  # Add evaluator email
                "evaluation_score": evaluation_score,
                "improvement_area": improvement_area,
                "improvement_feedback": improvement_feedback,
                "timestamp": datetime.now()
            }   

            # Save evaluation to firestore
            save_evaluation(evaluation_object)
            
            # Show success message
            st.success("Evaluation submitted successfully!")
            
            # Optional: Clear form by resetting session state
            st.session_state.content_loaded = False
            st.rerun()

# # # # # # # # # # #
# Main Function
# # # # # # # # # # #
def display_content():
    """Main function to display the evaluation page"""
        
    # Create containers
    description_container = st.empty()
    button_container = st.empty()
    content_container = st.empty()

    # Initialize states only if they don't exist
    if 'content_loaded' not in st.session_state:
        st.session_state.content_loaded = False
        st.session_state.current_case_study = None
        st.session_state.selected_area = "Accuracy"
        
    # Initial state - show button to load case study
    if not st.session_state.content_loaded:
        
        # Add description in its own container
        description_container.info("Click the button below to get a random case study to evaluate.")
        
        # Add button in separate container
        if button_container.button("Get Case Study to evaluate"):

            case_study = get_random_case_study()

            # Case study found
            if case_study:
                st.session_state.current_case_study = case_study
                st.session_state.content_loaded = True

            # Case study not found
            else:
                logger.error("Failed to load case study from database")
                st.error("No case studies found in the database")
    
    # Loaded state - show content and form
    if st.session_state.content_loaded:
                
        # Clear the initial view containers
        description_container.empty()
        button_container.empty()
        
        # Display the case study and evaluation form
        with content_container:
            col1, col2 = st.columns([6, 4])
            with col1:
                display_case_study(st.session_state.current_case_study)
            with col2:
                display_evaluation_form(st.session_state.current_case_study)
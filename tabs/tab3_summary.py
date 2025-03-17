import streamlit as st
from utils.firestore_manager import get_user_evaluations, delete_evaluation
import pandas as pd
import logging

# Configure logging
logger = logging.getLogger(__name__)

def display_content():
    logger.info("Displaying evaluation summary")
    st.header("Evaluation Summary")
    
    # Get all evaluations for the current user
    evaluations = get_user_evaluations(st.session_state.email)
    
    if not evaluations:
        logger.info(f"No evaluations found for user: {st.session_state.email}")
        st.info("You haven't submitted any evaluations yet.")
        return
    
    logger.info(f"Processing {len(evaluations)} evaluations for display")
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(evaluations)
    
    # Reorder and rename columns
    df = df[[
        'id', 'case_study_id', 'evaluation_score', 
        'improvement_area', 'improvement_feedback', 'timestamp',
        'case_study_url', 'case_study_content'
    ]].rename(columns={
        'id': 'Evaluation ID',
        'case_study_id': 'Case Study ID',
        'evaluation_score': 'Score',
        'improvement_area': 'Area for Improvement',
        'improvement_feedback': 'Feedback',
        'timestamp': 'Date',
        'case_study_url': 'Case Study URL',
        'case_study_content': 'Case Study Content'
    })
    
    # Format timestamp
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Display each evaluation in an expander
    for _, row in df.iterrows():
        
        with st.expander(f"Evaluation {row['Evaluation ID'][:8]}... - Score: {row['Score']}/10"):
            
            # Create tabs for evaluation details and case study content
            tab1, tab2 = st.tabs(["Evaluation Details", "Case Study Content"])
            
            with tab1:
                st.write(f"**Case Study ID:** {row['Case Study ID']}")
                st.write(f"**Case Study URL:** {row['Case Study URL']}")
                st.write(f"**Score:** {row['Score']}/10")
                st.write(f"**Area for Improvement:** {row['Area for Improvement']}")
                st.write(f"**Feedback:** {row['Feedback']}")
                st.write(f"**Date:** {row['Date']}")
                
                if st.button("Delete", key=f"delete_{row['Evaluation ID']}", type="secondary"):

                    logger.info(f"Delete button clicked for evaluation: {row['Evaluation ID']}")
                    
                    if delete_evaluation(row['Evaluation ID']):
                        logger.info(f"Successfully deleted evaluation: {row['Evaluation ID']}")
                        st.success("Evaluation deleted successfully!")
                        st.rerun()
                    
                    else:
                        logger.error(f"Failed to delete evaluation: {row['Evaluation ID']}")
                        st.error("Failed to delete evaluation.")
            
            with tab2:
                # Clean up the content by replacing separator lines with blank lines
                content = row['Case Study Content'].replace("- - - - - - - - -", "\n")
                st.markdown(content) 
import streamlit as st

def display_content():
        
    # Objective
    st.subheader("📋 Objective")
    st.info("""
    The objective of this evaluation process is to assess AI case studies for quality, 
    relevance, and suitability for publication on the GAiL Network website. 
    """)
    
    # Evaluation Steps
    st.subheader("🔄 Evaluation Process")
    st.info("""
    Follow these steps to evaluate a case study:
    
    1. **Navigate to Evaluation**: Select the 'Evaluation' tab to begin reviewing case studies
    2. **Generate Case Study**: Click the 'Get Case Study to evaluate' button to load a random case study
    3. **Review Content**: Read the case study thoroughly on the left side of the screen
    4. **Complete Evaluation Form**: On the right side:
       - Score the case study (1-10)
       - Select the area needing most improvement
       - Provide detailed feedback
    5. **Submit Feedback**: Click 'Submit Evaluation' to save your assessment
    6. Repeat the process for at least 10 case studies (so that you can get a good overview of the case studies)
    """)
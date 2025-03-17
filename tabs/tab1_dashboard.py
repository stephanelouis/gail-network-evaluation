import streamlit as st

def display_content():
    # Welcome and Introduction
    st.header("Welcome to the Case Study Evaluation Hub")
    
    # Info with button approach 1: Using columns
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("""
        This platform helps evaluate AI case studies for the GAiL Network. Your role is to review 
        case studies and provide feedback on their quality and suitability for publication.
        """)
    with col2:
        st.button("Start Evaluating", use_container_width=True)
    
    # How to Use This Platform
    st.subheader("📚 How to Use This Platform")
    
    # Step 1: Understanding Evaluation Criteria
    st.markdown("##### Step 1: Understanding the Evaluation Criteria")
    
    # Info with button approach 2: Sequential
    st.info("""
    When evaluating a case study, you'll be asked to:
    - Give an overall score (1-10)
    - Identify areas for improvement
    - Provide specific feedback and suggestions
    """)
    st.button("View Criteria Details", use_container_width=True)
    
    # Step 2: Evaluation Process
    st.markdown("##### Step 2: Following the Evaluation Process")
    st.write("""
    1. Go to the **Case Study Evaluation** tab
    2. Click '**Get Case Study**' to receive a case study for review
    3. Read the case study content (left side)
    4. Complete the evaluation form (right side)
    5. Submit your evaluation
    """)
    
    st.markdown("---")
    
    # Analytics Overview
    st.header("Evaluation Progress")
    
    # Add placeholder metrics (replace with actual data later)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Case Studies", value="--")
    with col2:
        st.metric(label="Your Evaluations", value="--")
    with col3:
        st.metric(label="Pending Reviews", value="--")
    
    # Distribution Information
    st.subheader("📊 Case Study Distribution")
    st.info("""
    View analytics by:
    - Industry sectors
    - Business functions
    - Business impact areas
    - Evaluation status
    """)
    
    # Note about data updates
    st.caption("Note: Analytics are updated in real-time as evaluations are submitted.") 
import streamlit as st

def display_content():

    st.subheader("Evaluation Summary")
    st.info("Once the feedbacks collected, this page will show:\n" +
            "- Overview of all evaluations\n" +
            "- Key areas of improvement\n" +
            "- Statistics by evaluator\n" +
            "- Detailed evaluation records") 
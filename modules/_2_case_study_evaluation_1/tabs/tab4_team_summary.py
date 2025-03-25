import streamlit as st
import logging

from utils.evaluation_helpers import get_all_evaluations, calculate_average_score, calculate_user_statistics
from utils.evaluation_helpers import analyze_top_scoring_evaluations, analyze_lowest_scoring_evaluations
from utils.evaluation_helpers import analyze_user_details, analyze_improvement_areas, analyze_improvement_areas_detailed

# Configure logging
logger = logging.getLogger(__name__)

def create_metric_card(title, value, description=""):
    """Create a card-like container for metrics"""
    
    # CSS to create a card-like effect
    st.markdown("""
        <style>
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-title {
            color: #0066cc;
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #1f1f1f;
            margin: 10px 0;
        }
        .metric-description {
            color: #666;
            font-size: 0.9em;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-description">{description}</div>
        </div>
    """, unsafe_allow_html=True)

def display_content():
    """Display the team summary content"""
    
    st.subheader("Team Evaluation Summary")
    
    if st.button('Show Results'):
        with st.spinner('Generating summary...'):

            try:
                # Fetch all evaluations
                evaluations = get_all_evaluations('evaluations', 'case_studies')
                
                # Create filtered dataset (excluding relevance)
                filtered_evaluations = [
                    eval for eval in evaluations 
                    if eval.get('improvement_area', '') != 'Relevance (Alignment with AI case study goals)'
                ]
                
                # Create a 4-column layout
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    create_metric_card(
                        "Total Evaluations",
                        len(evaluations),
                        "Total number of evaluations submitted"
                    )
                
                with col2:
                    create_metric_card(
                        "Evaluations (excl. Relevance)",
                        len(filtered_evaluations),
                        "Number of evaluations excluding relevance issues"
                    )
                
                with col3:
                    avg_score = calculate_average_score(evaluations)
                    create_metric_card(
                        "Team Average Score",
                        f"{avg_score}/10",
                        "Average score across all evaluations"
                    )
                
                with col4:
                    filtered_avg_score = calculate_average_score(filtered_evaluations)
                    create_metric_card(
                        "Average Score (excl. Relevance)",
                        f"{filtered_avg_score}/10",
                        "Average score excluding relevance issues"
                    )
                
                # User Statistics Card
                st.subheader("Users Analysis")
                user_stats = calculate_user_statistics(evaluations)
                if user_stats:
                    st.dataframe(
                        user_stats,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "User": st.column_config.TextColumn("User"),
                            "Forms Submitted": st.column_config.NumberColumn("Forms Submitted"),
                            "Average Score": st.column_config.TextColumn("Average Score"),
                            "Min Score": st.column_config.TextColumn("Min Score"),
                            "Max Score": st.column_config.TextColumn("Max Score")
                        }
                    )
                else:
                    st.info("No user statistics available yet.")
                
                # Detailed User Analysis
                st.subheader("Detailed User Analysis")
                user_details = analyze_user_details(evaluations)
                if user_details:
                    for user_data in user_details:
                        with st.expander(f"{user_data['user']} ({user_data['count']} evaluations)"):
                            st.markdown(f"### Total evaluations: {user_data['count']}")
                            st.markdown("---")
                            for eval in user_data['evaluations']:
                                timestamp_str = eval['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if eval['timestamp'] else 'No date'
                                
                                # Create tabs for each evaluation
                                eval_tab, case_tab = st.tabs(["Evaluation", "Case Study"])
                                
                                with eval_tab:
                                    st.markdown(f"""
                                        **{timestamp_str}** | Score: **{eval['score']}/10** | Area: **{eval['improvement_area']}**  
                                        🔗 {eval['source_url']}  
                                        _{eval['feedback']}_
                                    """)
                                
                                with case_tab:
                                    # Clean up the content by replacing separator lines with blank lines
                                    content = eval['case_study_final'].replace("- - - - - - - - -", "\n")
                                    st.markdown(content)
                                
                                st.markdown("---")
                else:
                    st.info("No detailed user analysis available yet.")
                
                # Improvement Areas Analysis
                st.subheader("Improvement Areas Analysis")
                improvement_areas = analyze_improvement_areas(evaluations)
                if improvement_areas:
                    st.dataframe(
                        improvement_areas,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "Improvement Area": st.column_config.TextColumn("Improvement Area"),
                            "Total Citations": st.column_config.NumberColumn("Total Citations"),
                            "Users Citing": st.column_config.TextColumn("Users Citing")
                        }
                    )
                else:
                    st.info("No improvement areas data available yet.")
                
                # Detailed Improvement Areas
                st.subheader("Detailed Improvement Areas Analysis")
                detailed_areas = analyze_improvement_areas_detailed(evaluations)
                if detailed_areas:
                    for area_data in detailed_areas:
                        with st.expander(f"{area_data['area']} (Cited {area_data['count']} times)"):
                            st.markdown(f"### Total citations: {area_data['count']}")
                            st.markdown("---")
                            sorted_feedbacks = sorted(
                                area_data['feedbacks'],
                                key=lambda x: (x['score'] if isinstance(x['score'], (int, float)) else 0,
                                            x['timestamp'] if x['timestamp'] else '0'),
                                reverse=True
                            )
                            for feedback in sorted_feedbacks:
                                timestamp_str = feedback['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if feedback['timestamp'] else 'No date'
                                
                                # Create tabs for each feedback
                                eval_tab, case_tab = st.tabs(["Evaluation", "Case Study"])
                                
                                with eval_tab:
                                    st.markdown(f"""
                                        **{timestamp_str}** | Score: **{feedback['score']}/10** | By: **{feedback['user']}**  
                                        🔗 {feedback['source_url']}  
                                        _{feedback['feedback']}_
                                    """)
                                
                                with case_tab:
                                    # Clean up the content by replacing separator lines with blank lines
                                    content = feedback.get('case_study_final', 'No summary available').replace("- - - - - - - - -", "\n")
                                    st.markdown(content)
                                
                                st.markdown("---")
                else:
                    st.info("No detailed feedback available yet.")
                
                # Add Top Scoring Evaluations section
                st.subheader("Top 10 Highest Scoring Evaluations")
                top_evaluations = analyze_top_scoring_evaluations(evaluations)
                
                if top_evaluations:
                    for eval in top_evaluations:
                        timestamp_str = eval['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if eval.get('timestamp') else 'No date'
                        score = eval.get('evaluation_score', 'N/A')
                        evaluator = eval.get('evaluator_email', 'Unknown')
                        
                        with st.expander(f"Score: {score}/10 - {timestamp_str} - By: {evaluator}"):
                            eval_tab, case_tab = st.tabs(["Evaluation", "Case Study"])
                            
                            with eval_tab:
                                st.markdown(f"""
                                    **Date:** {timestamp_str}  
                                    **Score:** {score}/10  
                                    **Area:** {eval.get('improvement_area', 'Not specified')}  
                                    **Evaluator:** {eval.get('evaluator_email', 'Unknown')}  
                                    🔗 {eval.get('source_url', 'No URL provided')}  
                                    
                                    _{eval.get('improvement_feedback', 'No feedback provided')}_
                                """)
                            
                            with case_tab:
                                # Clean up the content by replacing separator lines with blank lines
                                content = eval.get('case_study_final', 'No summary available').replace("- - - - - - - - -", "\n")
                                st.markdown(content)
                else:
                    st.info("No evaluations available yet.")
                
                # Add Lowest Scoring Evaluations section
                st.subheader("Top 10 Lowest Scoring Evaluations")
                lowest_evaluations = analyze_lowest_scoring_evaluations(evaluations)
                
                if lowest_evaluations:
                    for eval in lowest_evaluations:
                        timestamp_str = eval['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if eval.get('timestamp') else 'No date'
                        score = eval.get('evaluation_score', 'N/A')
                        evaluator = eval.get('evaluator_email', 'Unknown')
                        
                        with st.expander(f"Score: {score}/10 - {timestamp_str} - By: {evaluator}"):
                            eval_tab, case_tab = st.tabs(["Evaluation", "Case Study"])
                            
                            with eval_tab:
                                st.markdown(f"""
                                    **Date:** {timestamp_str}  
                                    **Score:** {score}/10  
                                    **Area:** {eval.get('improvement_area', 'Not specified')}  
                                    **Evaluator:** {eval.get('evaluator_email', 'Unknown')}  
                                    🔗 {eval.get('source_url', 'No URL provided')}  
                                    
                                    _{eval.get('improvement_feedback', 'No feedback provided')}_
                                """)
                            
                            with case_tab:
                                # Clean up the content by replacing separator lines with blank lines
                                content = eval.get('case_study_final', 'No summary available').replace("- - - - - - - - -", "\n")
                                st.markdown(content)
                else:
                    st.info("No evaluations available yet.")
                
            except Exception as e:
                logger.error(f"Error generating summary: {str(e)}")
                st.error("An error occurred while generating the summary. Please try again.")

import streamlit as st
import logging
from utils.firestore_manager import get_db
from statistics import mean
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

def get_all_evaluations():
    """Fetch all evaluations using the firestore manager's db connection and merge with case study information"""

    try:
        
        db = get_db()
        evaluations_ref = db.collection('evaluations')
        case_studies_ref = db.collection('case_studies')
        
        # Create a dictionary of case studies with their URLs and summaries
        case_studies = {}
        for case in case_studies_ref.stream():
            case_data = case.to_dict()
            case_studies[case.id] = {
                'source_url': case_data.get('source_url', 'No URL provided'),
                'case_study_final': case_data.get('case_study_final', 'No summary available')
            }
        
        # Fetch evaluations and merge with case study data
        evaluations = []
        for eval in evaluations_ref.stream():
            eval_data = eval.to_dict()
            case_study_id = eval_data.get('case_study_id')
            
            # Add case study data if available
            if case_study_id and case_study_id in case_studies:
                eval_data['source_url'] = case_studies[case_study_id]['source_url']
                eval_data['case_study_final'] = case_studies[case_study_id]['case_study_final']
            else:
                eval_data['source_url'] = 'No URL provided'
                eval_data['case_study_final'] = 'No summary available'
            
            evaluations.append(eval_data)
        
        return evaluations
    
    except Exception as e:
        logger.error(f"Error fetching evaluations: {str(e)}")
        return []

def calculate_average_score(evaluations):
    """Calculate the average score from evaluations"""

    try:
        scores = [eval['evaluation_score'] for eval in evaluations if 'evaluation_score' in eval]
        if scores:
            return round(mean(scores), 1)
        return 0
    
    except Exception as e:
        logger.error(f"Error calculating average score: {str(e)}")
        return 0

def analyze_improvement_areas(evaluations):
    """Analyze improvement areas and their citations"""
    try:
        # Group by improvement area
        area_stats = defaultdict(lambda: {'count': 0, 'users': defaultdict(int)})
        
        for eval in evaluations:
            if 'improvement_area' in eval and 'evaluator_email' in eval:
                area = eval['improvement_area']
                user = eval['evaluator_email']
                area_stats[area]['count'] += 1
                area_stats[area]['users'][user] += 1
        
        # Format results
        area_summaries = []
        for area, stats in area_stats.items():
            # Format user citations
            user_citations = []
            for user, count in stats['users'].items():
                user_citations.append(f"{user} ({count})")
            
            area_summaries.append({
                'Improvement Area': area,
                'Total Citations': stats['count'],
                'Users Citing': ', '.join(user_citations)
            })
        
        # Sort by total citations (descending)
        return sorted(area_summaries, key=lambda x: x['Total Citations'], reverse=True)
    
    except Exception as e:
        logger.error(f"Error analyzing improvement areas: {str(e)}")
        return []

def analyze_improvement_areas_detailed(evaluations):
    """Analyze improvement areas with detailed feedback"""
    try:
        # Group by improvement area
        area_stats = defaultdict(lambda: {
            'count': 0,
            'users': defaultdict(int),
            'feedbacks': []  # List to store feedback details
        })
        
        for eval in evaluations:
            if 'improvement_area' in eval and 'evaluator_email' in eval:
                area = eval['improvement_area']
                user = eval['evaluator_email']
                feedback = eval.get('improvement_feedback', 'No feedback provided')
                timestamp = eval.get('timestamp', None)
                score = eval.get('evaluation_score', 'N/A')  # Get the score
                source_url = eval.get('source_url', 'No URL provided')  # Add source URL
                
                area_stats[area]['count'] += 1
                area_stats[area]['users'][user] += 1
                area_stats[area]['feedbacks'].append({
                    'user': user,
                    'feedback': feedback,
                    'timestamp': timestamp,
                    'score': score,
                    'source_url': source_url  # Add source URL to feedbacks
                })
        
        # Format results
        area_summaries = []
        for area, stats in area_stats.items():
            # Sort feedbacks by score (highest first), then by timestamp
            feedbacks = sorted(stats['feedbacks'], 
                            key=lambda x: (x['score'] if isinstance(x['score'], (int, float)) else 0,
                                        x['timestamp'] if x['timestamp'] else '0'),
                            reverse=True)
            
            area_summaries.append({
                'area': area,
                'count': stats['count'],
                'feedbacks': feedbacks
            })
        
        # Sort by count (descending)
        return sorted(area_summaries, key=lambda x: x['count'], reverse=True)
    
    except Exception as e:
        logger.error(f"Error analyzing detailed improvement areas: {str(e)}")
        return []

def calculate_user_statistics(evaluations):
    """Calculate statistics per user"""

    try:
        # Group evaluations by user
        user_stats = defaultdict(lambda: {'scores': [], 'count': 0})
        
        for eval in evaluations:
            if 'evaluator_email' in eval and 'evaluation_score' in eval:
                email = eval['evaluator_email']
                user_stats[email]['scores'].append(eval['evaluation_score'])
                user_stats[email]['count'] += 1
        
        # Calculate statistics and format results
        user_summaries = []
        for email, stats in user_stats.items():
            scores = stats['scores']
            user_summaries.append({
                'User': email,
                'Forms Submitted': stats['count'],
                'Average Score': f"{round(mean(scores), 1)}/10" if scores else "0/10",
                'Min Score': f"{min(scores)}/10" if scores else "N/A",
                'Max Score': f"{max(scores)}/10" if scores else "N/A"
            })
        
        # Sort alphabetically by email
        return sorted(user_summaries, key=lambda x: x['User'].lower())
    
    except Exception as e:
        logger.error(f"Error calculating user statistics: {str(e)}")
        return []

def analyze_user_details(evaluations):
    """Analyze detailed user evaluations"""
    try:
        # Group by user
        user_details = defaultdict(lambda: {
            'count': 0,
            'evaluations': []
        })
        
        for eval in evaluations:
            if 'evaluator_email' in eval:
                user = eval['evaluator_email']
                user_details[user]['count'] += 1
                user_details[user]['evaluations'].append({
                    'improvement_area': eval.get('improvement_area', 'Not specified'),
                    'feedback': eval.get('improvement_feedback', 'No feedback provided'),
                    'score': eval.get('evaluation_score', 0),  # Default to 0 for sorting
                    'timestamp': eval.get('timestamp', None),
                    'source_url': eval.get('source_url', 'No URL provided'),
                    'case_study_final': eval.get('case_study_final', 'No summary available')
                })
        
        # Format and sort evaluations for each user
        user_summaries = []
        for user, details in user_details.items():
            # Sort evaluations by score (highest first), then by timestamp if scores are equal
            evaluations = sorted(details['evaluations'],
                              key=lambda x: (x['score'] if isinstance(x['score'], (int, float)) else 0, 
                                          x['timestamp'] if x['timestamp'] else '0'),
                              reverse=True)
            
            user_summaries.append({
                'user': user,
                'count': details['count'],
                'evaluations': evaluations
            })
        
        # Sort by user email
        return sorted(user_summaries, key=lambda x: x['user'].lower())
    
    except Exception as e:
        logger.error(f"Error analyzing user details: {str(e)}")
        return []

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

def analyze_top_scoring_evaluations(evaluations, limit=10):
    """Analyze and return the top scoring evaluations"""
    try:
        # Filter out evaluations without scores and sort them
        scored_evaluations = [
            eval for eval in evaluations 
            if 'evaluation_score' in eval and eval['evaluation_score'] is not None
        ]
        
        # Sort by score (highest first) and timestamp
        sorted_evaluations = sorted(
            scored_evaluations,
            key=lambda x: (x['evaluation_score'], x['timestamp'] if 'timestamp' in x else '0'),
            reverse=True
        )
        
        # Return top N evaluations
        return sorted_evaluations[:limit]
    
    except Exception as e:
        logger.error(f"Error analyzing top scoring evaluations: {str(e)}")
        return []

def analyze_lowest_scoring_evaluations(evaluations, limit=10):
    """Analyze and return the lowest scoring evaluations"""
    try:
        # Filter out evaluations without scores and sort them
        scored_evaluations = [
            eval for eval in evaluations 
            if 'evaluation_score' in eval and eval['evaluation_score'] is not None
        ]
        
        # Sort by score (lowest first) and timestamp
        sorted_evaluations = sorted(
            scored_evaluations,
            key=lambda x: (x['evaluation_score'], x['timestamp'] if 'timestamp' in x else '0')
        )
        
        # Return bottom N evaluations
        return sorted_evaluations[:limit]
    
    except Exception as e:
        logger.error(f"Error analyzing lowest scoring evaluations: {str(e)}")
        return []

def display_content():
    """Display the team summary content"""
    
    st.subheader("Team Evaluation Summary")
    
    if st.button('Show Summary Cards'):
        with st.spinner('Generating summary...'):

            try:
                # Fetch all evaluations
                evaluations = get_all_evaluations()
                
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

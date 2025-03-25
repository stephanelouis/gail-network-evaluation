from collections import defaultdict
from statistics import mean

from utils.firestore_manager import get_db

# Configure logging
import logging
logger = logging.getLogger(__name__)

def get_all_evaluations(evaluations_collection_name, case_studies_collection_name):
    """Fetch all evaluations using the firestore manager's db connection and merge with case study information"""

    try:
        
        db = get_db()
        evaluations_ref = db.collection(evaluations_collection_name)
        case_studies_ref = db.collection(case_studies_collection_name)
        
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
    """
    Calculate the average score from evaluations, where each evaluator's contribution
    is weighted equally regardless of how many evaluations they submitted.
    Returns the mean of individual evaluator means.
    """
    try:

        # Group evaluations by evaluator
        evaluator_scores = defaultdict(list)
        
        # Collect all scores for each evaluator
        for eval in evaluations:
            if 'evaluation_score' in eval and 'evaluator_email' in eval:
                email = eval['evaluator_email']
                score = eval['evaluation_score']
                evaluator_scores[email].append(score)
        
        # Calculate average for each evaluator
        evaluator_averages = []
        for email, scores in evaluator_scores.items():
            evaluator_avg = mean(scores)
            evaluator_averages.append(evaluator_avg)
            logger.info(f"Evaluator {email}: average score {round(evaluator_avg, 1)} from {len(scores)} evaluations")
        
        # Calculate overall average (mean of evaluator means)
        if evaluator_averages:
            overall_avg = mean(evaluator_averages)
            logger.info(f"Overall average (across {len(evaluator_averages)} evaluators): {round(overall_avg, 1)}")
            return round(overall_avg, 1)
            
        return 0
    
    except Exception as e:
        logger.error(f"Error calculating average score: {str(e)}")
        return 0

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

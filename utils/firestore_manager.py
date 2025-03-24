"""
Firestore Manager for the Case Study Evaluation Hub.
Handles all Firestore operations.
"""
import firebase_admin
from firebase_admin import credentials, firestore
import json
import logging
import os
import streamlit as st
from typing import Dict, Any, Optional, List

from utils.url_helper import URLHelper

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Firebase
def get_firebase_credentials():
    """Get Firebase credentials from either local file or Streamlit secrets"""
    
    # Try local credentials first
    local_creds_path = "config/firebase-credentials.json"
    if os.path.exists(local_creds_path):
        with open(local_creds_path, 'r') as f:
            return json.load(f)
    
    # Fall back to Streamlit secrets
    if st.secrets and "FIREBASE_CREDENTIALS" in st.secrets:
        creds = st.secrets["FIREBASE_CREDENTIALS"]
        if isinstance(creds, str):
            try:
                return json.loads(creds)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse credentials JSON from Streamlit secrets: {str(e)}")
                st.error(f"Failed to parse credentials JSON from Streamlit secrets: {str(e)}")
                st.stop()
        return creds
    
    logger.error("Firebase credentials not found")
    st.error("⚠️ Firebase credentials not found. Please configure them in Streamlit Cloud or add a local config/firebase-credentials.json file.")
    st.stop()

try:
    app = firebase_admin.get_app()
except ValueError:
    try:
        # Get credentials from either local file or Streamlit secrets
        creds = get_firebase_credentials()
        
        # Initialize Firebase
        cred = credentials.Certificate(creds)
        app = firebase_admin.initialize_app(cred)
        logger.info(f"Firebase initialized with project: {creds.get('project_id')}")
        st.write(f"Firebase initialized with project: {creds.get('project_id')}")
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        st.error(f"⚠️ Failed to initialize Firebase: {str(e)}")
        st.stop()

db = firestore.client()

def get_db():
    """Get or initialize Firestore database"""
    return db

def get_random_case_study() -> Optional[Dict[str, Any]]:
    """
    Fetch a random case study from Firestore that hasn't been evaluated yet.
    Returns None if no case studies are found.
    """
    try:
        
        # Use get_unevaluated_case_study to get a random case study that hasn't been evaluated
        case_study = get_unevaluated_case_study(st.session_state.email)
        
        if case_study is None:
            st.error("No unevaluated case studies found in database")
            return None
            
        return case_study
        
    except Exception as e:
        st.error(f"Error processing get_random_case_study(): {str(e)}")
        return None

def save_evaluation(evaluation_data: Dict[str, Any]) -> bool:
    """
    Save an evaluation to Firestore.
    Args:
        evaluation_data: Dictionary containing:
            - id: The evaluation ID (pre-generated)
            - user_email: Email of the evaluator
            - case_study_id: ID of the evaluated case study
            - evaluation_score: Integer score from 1-10
            - improvement_area: Selected improvement area
            - improvement_feedback: Detailed feedback text
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        
        # Use the pre-generated ID from the evaluation data
        evaluation_id = evaluation_data['id']
        
        # Add timestamp to the evaluation data
        evaluation_data['timestamp'] = firestore.SERVER_TIMESTAMP
        
        # Save to Firestore with the pre-generated ID
        db.collection('evaluations').document(evaluation_id).set(evaluation_data)
        logger.info(f"Successfully saved evaluation with ID: {evaluation_id}")

        return True
    except Exception as e:
        logger.error(f"Error saving evaluation: {str(e)}")
        st.error(f"Error processing save_evaluation(): {str(e)}")
        return False

def get_unevaluated_case_study(user_email: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a random case study that hasn't been evaluated by the given user.
    Args:
        user_email: Email of the user
    Returns:
        Optional[Dict[str, Any]]: A case study dictionary or None if no unevaluated cases found
    """
    try:
        
        # Get all case study IDs this user has evaluated
        evaluated_refs = db.collection('evaluations')\
            .where('user_email', '==', user_email)\
            .select('case_study_id')\
            .get()
        
        evaluated_ids = {eval.to_dict()['case_study_id'] for eval in evaluated_refs}
        
        # Get all case studies
        all_cases = db.collection('case_studies').get()
        available_cases = []
        
        # Filter out evaluated ones
        for doc in all_cases:
            if doc.id not in evaluated_ids:
                case_study = doc.to_dict()
                case_study['id'] = doc.id
                available_cases.append(case_study)
        
        # Return a random one if any available
        if available_cases:
            from random import choice
            return choice(available_cases)
        
        return None
        
    except Exception as e:
        st.error(f"Error processing get_unevaluated_case_study(): {str(e)}")
        return None

def get_user_evaluations_count(user_email):
    """Get the number of case studies reviewed by a specific user"""
    try:
        # Query evaluations collection for the user's email
        evaluations_ref = db.collection('evaluations')
        query = evaluations_ref.where('evaluator_email', '==', user_email)
        evaluations = query.get()
        
        return len(evaluations)
    except Exception as e:
        logger.error(f"Error getting user evaluations count: {e}")
        return 0

def get_user_evaluations(user_email):
    """Get all evaluations provided by a specific user"""
    
    try:
        logger.info(f"Fetching evaluations for user: {user_email}")
        # Query evaluations collection for the user's email
        evaluations_ref = db.collection('evaluations')
        query = evaluations_ref.where('evaluator_email', '==', user_email)
        evaluations = query.get()
        
        # Convert to list of dictionaries with document IDs and case study data
        result = []
        for eval in evaluations:

            # Convert to dictionary
            eval_dict = eval.to_dict()
            # Get the case study document
            case_study_doc = db.collection('case_studies').document(eval_dict['case_study_id']).get()
            if case_study_doc.exists:
                case_study_data = case_study_doc.to_dict()
                eval_dict['case_study_url'] = case_study_data.get('source_url', 'N/A')
                eval_dict['case_study_content'] = case_study_data.get('case_study_final', 'N/A')
            else:
                eval_dict['case_study_url'] = 'N/A'
                eval_dict['case_study_content'] = 'N/A'
            
            # Add the evaluation ID
            result.append({
                'id': eval.id,
                **eval_dict
            })
        
        logger.info(f"Found {len(result)} evaluations for user {user_email}")
        return result
    
    except Exception as e:
        logger.error(f"Error getting user evaluations: {str(e)}")
        return []

def delete_evaluation(evaluation_id):
    """Delete an evaluation by its ID"""
    try:
        logger.info(f"Attempting to delete evaluation: {evaluation_id}")
        db.collection('evaluations').document(evaluation_id).delete()
        logger.info(f"Successfully deleted evaluation: {evaluation_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting evaluation {evaluation_id}: {str(e)}")
        return False

def get_one_case_study_per_company() -> List[Dict[str, Any]]:
    """
    Retrieve one case study per company from Firestore.
    Returns a list of dictionaries containing case study data grouped by company URL.
    """
    try:
        db = get_db()
        if db is None:
            logger.error("Database connection failed")
            return []

        # Get all case studies
        case_studies = db.collection('case_studies_v2').get()
        if case_studies is None:
            logger.error("Failed to fetch case studies")
            return []

        # Convert to list of dictionaries and group by clean URL
        url_cases = {}
        for doc in case_studies:
            try:
                data = doc.to_dict()
                if not data:
                    continue
                    
                source_url = data.get('source_url')
                if not source_url:
                    continue
                    
                clean_url = URLHelper.clean_url(source_url)
                if not clean_url:
                    continue
                    
                # Only keep the first case study for each clean URL
                if clean_url not in url_cases:
                    data['id'] = doc.id
                    url_cases[clean_url] = data
                    
            except Exception as e:
                logger.error(f"Error processing case study {doc.id}: {str(e)}")
                continue

        # Convert to list of case studies
        return list(url_cases.values())

    except Exception as e:
        logger.error(f"Error getting case studies by company: {str(e)}")
        return [] 
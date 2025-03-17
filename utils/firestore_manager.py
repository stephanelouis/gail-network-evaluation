"""
Firestore Manager for the Case Study Evaluation Hub.
Handles all Firestore operations.
"""

import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Any, Optional
import pandas as pd
import streamlit as st

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
                st.error(f"Failed to parse credentials JSON from Streamlit secrets: {str(e)}")
                st.stop()
        return creds
    
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
        st.write(f"Firebase initialized with project: {creds.get('project_id')}")
        
    except Exception as e:
        st.error(f"⚠️ Failed to initialize Firebase: {str(e)}")
        st.stop()

db = firestore.client()

def get_db():
    """Get or initialize Firestore database"""
    return db

def get_case_studies_stats() -> Dict[str, Any]:
    """
    Retrieve statistics about case studies from Firestore.
    Returns a dictionary containing various statistics and distributions.
    """
    try:
        
        db = get_db()
        # Get all case studies
        case_studies = db.collection('case_studies').get()
        evaluations = db.collection('evaluations').get()

        # Convert to list of dictionaries
        case_studies_data = [doc.to_dict() for doc in case_studies]
        evaluations_data = [doc.to_dict() for doc in evaluations]

        # Basic counts
        total_cases = len(case_studies_data)
        evaluated_cases = len(set(eval['case_study_id'] for eval in evaluations_data))
        
        # Create distributions
        industry_dist = {}
        business_functions_dist = {}
        business_impacts_dist = {}

        for case in case_studies_data:
            # Industry distribution
            industry = case.get('case_study_classification', {}).get('industry', {}).get('industry_classification')
            if industry:
                industry_dist[industry] = industry_dist.get(industry, 0) + 1

            # Business functions distribution
            functions = case.get('case_study_classification', {}).get('business_functions', [])
            for func in functions:
                if func:
                    business_functions_dist[func] = business_functions_dist.get(func, 0) + 1

            # Business impacts distribution
            impacts = case.get('case_study_classification', {}).get('business_impacts', [])
            for impact in impacts:
                if impact:
                    business_impacts_dist[impact] = business_impacts_dist.get(impact, 0) + 1

        # Create detailed DataFrame
        detailed_data = pd.DataFrame(case_studies_data)

        return {
            "total_case_studies": total_cases,
            "evaluated_case_studies": evaluated_cases,
            "pending_evaluations": total_cases - evaluated_cases,
            "industry_distribution": industry_dist,
            "business_functions": business_functions_dist,
            "business_impacts": business_impacts_dist,
            "detailed_data": detailed_data if not detailed_data.empty else None
        }

    except Exception as e:
        return {
            "total_case_studies": 0,
            "evaluated_case_studies": 0,
            "pending_evaluations": 0,
            "industry_distribution": {},
            "business_functions": {},
            "business_impacts": {},
            "detailed_data": None
        }

def get_random_case_study() -> Optional[Dict[str, Any]]:
    """
    Fetch a random case study from Firestore that hasn't been evaluated yet.
    Returns None if no case studies are found.
    """
    try:
        
        # Get all documents from case_studies collection
        docs = list(db.collection('case_studies').stream())
        
        if not docs:
            st.error("No case studies found in database")
            return None
            
        # Select a random document
        from random import choice
        doc = choice(docs)
        
        # Convert to dictionary and add ID
        case_study = doc.to_dict()
        case_study['id'] = doc.id
        
        return case_study
        
    except Exception as e:
        st.error(f"Error processing get_random_case_study(): {str(e)}")
        return None

def save_evaluation(evaluation_data: Dict[str, Any]) -> bool:
    """
    Save an evaluation to Firestore.
    Args:
        evaluation_data: Dictionary containing:
            - user_email: Email of the evaluator
            - case_study_id: ID of the evaluated case study
            - evaluation_score: Integer score from 1-10
            - improvement_area: Selected improvement area
            - improvement_feedback: Detailed feedback text
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:

        # Add timestamp to the evaluation data
        evaluation_data['timestamp'] = firestore.SERVER_TIMESTAMP
        
        # Save to Firestore
        db.collection('evaluations').add(evaluation_data)

        return True
    except Exception as e:
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
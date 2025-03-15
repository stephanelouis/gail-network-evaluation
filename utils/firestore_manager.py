"""
Firestore Manager for the Case Study Evaluation Hub.
Handles all Firestore operations.
"""

import json
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Any, Optional
import pandas as pd
import streamlit as st

# Global variables
_db = None

def get_db():
    """Get or initialize Firestore database"""
    global _db
    if _db is None:
        try:
            
            # First try to get existing app
            app = firebase_admin.get_app()
            st.write("Using existing Firebase app")
        except ValueError:
            try:
                # Try to get credentials from Streamlit secrets
                if not hasattr(st, 'secrets') or 'FIREBASE_CREDENTIALS' not in st.secrets:
                    raise ValueError("No Firebase credentials found in Streamlit secrets")
                
                st.write("Initializing Firebase with Streamlit secrets")
                cred_dict = st.secrets["FIREBASE_CREDENTIALS"]
                if isinstance(cred_dict, str):
                    try:
                        cred_dict = json.loads(cred_dict)
                    except json.JSONDecodeError as e:
                        st.error("Failed to parse Firebase credentials from secrets")
                        raise ValueError(f"Invalid Firebase credentials format: {str(e)}")
                
                cred = credentials.Certificate(cred_dict)
                app = firebase_admin.initialize_app(cred)
                st.write(f"Successfully initialized Firebase with project ID: {cred_dict.get('project_id')}")
                
            except Exception as e:
                st.error(f"Failed to initialize Firebase: {str(e)}")
                st.error("Please ensure Firebase credentials are properly configured in Streamlit secrets")
                raise
        
        _db = firestore.client()
    return _db

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
        print(f"Error getting case studies stats: {e}")
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

        db = get_db()
        st.write("Attempting to fetch case studies...")
        
        # Get all documents from case_studies collection
        collection_ref = db.collection('case_studies')
        st.write(f"Querying collection: {collection_ref.path}")
        
        docs = collection_ref.limit(1).stream()
        doc_list = list(docs)  # Convert to list to check length
        st.write(f"Found {len(doc_list)} documents")
        
        # Get the first document if available
        if doc_list:
            doc = doc_list[0]
            case_study = doc.to_dict()
            case_study['id'] = doc.id
            st.write(f"Retrieved case study with ID: {doc.id}")
            return case_study
            
        st.write("No documents found in case_studies collection")
        return None
    
    except Exception as e:
        st.error(f"Error fetching case study: {str(e)}")
        return None 
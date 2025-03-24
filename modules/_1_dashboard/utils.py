from typing import Dict, Any
import pandas as pd
import logging

from utils.firestore_manager import get_db
from utils.url_helper import URLHelper
from utils.helpers import load_company_urls

# Configure logging
logger = logging.getLogger(__name__)

def _calculate_company_distribution(case_studies_data: list) -> dict:
    """Calculate company distribution from case studies data."""

    # Initialize distribution with URLs from config file
    company_dist = {}
    try:
        config_urls = load_company_urls()
        if config_urls:
            # Initialize all configured URLs with count 0
            for url in config_urls:
                clean_url = URLHelper.clean_url(url)
                if clean_url:
                    company_dist[clean_url] = 0
    except Exception as e:
        logger.error(f"Error loading company URLs from config: {str(e)}")

    if not case_studies_data:
        return company_dist
        
    for case in case_studies_data:
        try:
            if not isinstance(case, dict):
                continue
            url = case.get('source_url')
            if not isinstance(url, str):
                continue
            if url:
                # Extract domain from URL and use it as the key
                clean_url = URLHelper.clean_url(url)
                if clean_url:  # Only add if we got a valid URL
                    company_dist[clean_url] = company_dist.get(clean_url, 0) + 1
        except Exception as e:
            logger.error(f"Error calculating company distribution for case: {str(e)}")
            continue
    
    return company_dist

def _calculate_sector_distribution(case_studies_data: list) -> dict:
    """Calculate sector distribution from case studies data."""

    sector_dist = {}
    
    if not case_studies_data:
        return sector_dist
        
    for case in case_studies_data:
        try:
            if not isinstance(case, dict):
                continue
            classification = case.get('classification')
            if not isinstance(classification, dict):
                continue
            industry = classification.get('industry')
            if not isinstance(industry, dict):
                continue
            sector = industry.get('category')
            if sector:
                sector_dist[sector] = sector_dist.get(sector, 0) + 1
        except Exception as e:
            logger.error(f"Error calculating sector distribution for case: {str(e)}")
            continue
    return sector_dist

def _calculate_industry_distribution(case_studies_data: list) -> dict:
    """Calculate industry distribution from case studies data."""
    
    industry_dist = {}
    if not case_studies_data:
        return industry_dist
        
    for case in case_studies_data:
        try:
            if not isinstance(case, dict):
                continue
            classification = case.get('classification')
            if not isinstance(classification, dict):
                continue
            industry = classification.get('industry')
            if not isinstance(industry, dict):
                continue
            sector = industry.get('category')
            subcategory = industry.get('subcategory')
            if sector and subcategory:
                key = f"{subcategory} ({sector})"
                industry_dist[key] = industry_dist.get(key, 0) + 1
        except Exception as e:
            logger.error(f"Error calculating industry distribution for case: {str(e)}")
            continue
    
    return industry_dist

def _calculate_business_functions_distribution(case_studies_data: list) -> dict:
    """Calculate business functions distribution from case studies data."""

    business_functions_dist = {}
    if not case_studies_data:
        return business_functions_dist
        
    for case in case_studies_data:
        try:
            if not isinstance(case, dict):
                continue
            classification = case.get('classification')
            if not isinstance(classification, dict):
                continue
            functions = classification.get('business_functions', [])
            if not isinstance(functions, list):
                continue
            for func in functions:
                if not isinstance(func, dict):
                    continue
                category = func.get('category')
                subcategory = func.get('subcategory')
                if category and subcategory:
                    key = f"{subcategory} ({category})"
                    business_functions_dist[key] = business_functions_dist.get(key, 0) + 1
        except Exception as e:
            logger.error(f"Error calculating business functions distribution for case: {str(e)}")
            continue
    
    return business_functions_dist

def _calculate_business_impacts_distribution(case_studies_data: list) -> dict:
    """Calculate business impacts distribution from case studies data."""

    business_impacts_dist = {}
    if not case_studies_data:
        return business_impacts_dist
        
    for case in case_studies_data:
        try:
            if not isinstance(case, dict):
                continue
            classification = case.get('classification')
            if not isinstance(classification, dict):
                continue
            impacts = classification.get('business_impacts', [])
            if not isinstance(impacts, list):
                continue
            for impact in impacts:
                if not isinstance(impact, dict):
                    continue
                category = impact.get('category')
                subcategory = impact.get('subcategory')
                if category and subcategory:
                    key = f"{subcategory} ({category})"
                    business_impacts_dist[key] = business_impacts_dist.get(key, 0) + 1
        except Exception as e:
            logger.error(f"Error calculating business impacts distribution for case: {str(e)}")
            continue
    
    return business_impacts_dist

def _calculate_maturity_model_distribution(case_studies_data: list) -> dict:
    """Calculate maturity model distribution from case studies data."""

    maturity_model_dist = {}
    if not case_studies_data:
        return maturity_model_dist
        
    for case in case_studies_data:
        try:
            if not isinstance(case, dict):
                continue
            classification = case.get('classification')
            if not isinstance(classification, dict):
                continue
            models = classification.get('maturity_models', [])
            if not isinstance(models, list):
                continue
            for model in models:
                if not isinstance(model, dict):
                    continue
                level = model.get('level')
                category = model.get('category')
                subcategory = model.get('subcategory')
                if level and category and subcategory:
                    key = f"{subcategory} ({level} - {category})"
                    maturity_model_dist[key] = maturity_model_dist.get(key, 0) + 1
        except Exception as e:
            logger.error(f"Error calculating maturity model distribution for case: {str(e)}")
            continue
    
    return maturity_model_dist

def get_case_studies_stats() -> Dict[str, Any]:
    """
    Retrieve statistics about case studies from Firestore.
    Returns a dictionary containing various statistics and distributions.
    """
    # Initialize empty return dictionary
    empty_stats = {
        "total_case_studies": 0,
        "evaluated_case_studies": 0,
        "pending_evaluations": 0,
        "company_distribution": {},
        "sector_distribution": {},
        "industry_distribution": {},
        "business_functions": {},
        "business_impacts": {},
        "maturity_models": {},
        "detailed_data": None
    }
    
    try:

        db = get_db()
        if db is None:
            logger.error("Database connection failed")
            return empty_stats

        # Get all case studies
        case_studies = db.collection('case_studies_v2').get()
        if case_studies is None:
            logger.error("Failed to fetch case studies")
            return empty_stats
            
        evaluations = db.collection('evaluations').get()
        if evaluations is None:
            logger.error("Failed to fetch evaluations")
            return empty_stats

        # Convert to list of dictionaries
        case_studies_data = [doc.to_dict() for doc in case_studies]
        evaluations_data = [doc.to_dict() for doc in evaluations]
        
        # Basic counts
        total_cases = len(case_studies_data)
        evaluated_cases = len(set(eval.get('case_study_id') for eval in evaluations_data if eval.get('case_study_id')))
        
        # Calculate distributions
        company_dist = _calculate_company_distribution(case_studies_data)
        print(company_dist)
        sector_dist = _calculate_sector_distribution(case_studies_data)
        industry_dist = _calculate_industry_distribution(case_studies_data)
        business_functions_dist = _calculate_business_functions_distribution(case_studies_data)
        business_impacts_dist = _calculate_business_impacts_distribution(case_studies_data)
        maturity_model_dist = _calculate_maturity_model_distribution(case_studies_data)

        # Create detailed DataFrame
        detailed_data = pd.DataFrame(case_studies_data)

        # Return the data
        return {
            "total_case_studies": total_cases,
            "evaluated_case_studies": evaluated_cases,
            "pending_evaluations": total_cases - evaluated_cases,
            "company_distribution": company_dist,
            "sector_distribution": sector_dist,
            "industry_distribution": industry_dist,
            "business_functions": business_functions_dist,
            "business_impacts": business_impacts_dist,
            "maturity_models": maturity_model_dist,
            "detailed_data": detailed_data if not detailed_data.empty else None
        }

    except Exception as e:
        logger.error(f"Error getting case studies stats: {str(e)}")
        return empty_stats
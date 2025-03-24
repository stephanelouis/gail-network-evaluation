"""
= = = = = = = = = = = =
URLHelper
= = = = = = = = = = = =

**Description**
This class provides a helper to extract a domain name from a given URL.  

**Comments from Previous Implementation**
The original codebase from thegenaifrontier was refactored in a staticmethod.

Author:        Stéphane Bouvier
Created On:    2025-02-24         
Last Updated:  2025-03-24   
Version:       1.0.0
"""

import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class URLHelper:
    @staticmethod
    def extract_domain(url: str) -> str:
        try:
            parsed_url = urlparse(url)
            domain_parts = parsed_url.netloc.split('.')
                        
            # Return full domain with subdomain
            return parsed_url.netloc  # Return domain as is if already correct

        except Exception as e:
            logging.error(f"Error processing URLHelper.extract_domain from URL '{url}': {e}")
            return ""
        
    @staticmethod
    def clean_url(url: str) -> str:
        try:
            return f"https://{URLHelper.extract_domain(url)}"
        except Exception as e:
            logging.error(f"Error processing URLHelper.clean_url from URL '{url}': {e}")
            return url 
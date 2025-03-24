"""
= = = = = = = = = = = =
Shared Agent Utilities
= = = = = = = = = = = =

This module contains a function to format case study summaries for side-by-side comparison.

Author:        Stéphane Bouvier
Created On:    2025-03-24
Version:       1.0.0
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

def format_case_study_summary(case_study: Dict) -> str:
    """
    Format case study summary from webpage data in a consistent way for all classifiers.
    """
    try:
        
        output = []

        title = case_study.get('title', None)
        introduction = case_study.get('introduction', None)
        sections = case_study.get('sections', [])

        # Add title
        if title:
            output.append(f"**{title}**")
            output.append("")

        # Add introduction
        if introduction:
            output.append(f"{introduction}")
            output.append("")

        # Format sections
        for section in sections:

            if section.get("section_title"):
                output.append(f"# {section['section_title']}")
                output.append("")
            
            # Add section introduction
            if section.get("section_introduction"):
                output.append(section["section_introduction"])
                output.append("")
            
            # Add section content
            if section.get("section_content"):
                for point in section["section_content"]:
                    if point:
                        output.append(f"- {point}")
                output.append("")

        output_formatted = "\n".join(output)
        
        # Return formatted case study summary
        return output_formatted
    
    except Exception as e:
        return "" 
# src/utils/report_utils.py
from typing import List, Dict
import re

def clean_markdown(text: str) -> str:
    """Clean and standardize markdown formatting"""
    # Remove multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Ensure proper spacing around headers
    text = re.sub(r'(#{1,6} .+?)(\n[^#\n])', r'\1\n\2', text)

    return text.strip()

def extract_sections(text: str) -> List[Dict[str, str]]:
    """Extract sections from markdown text"""
    sections = []
    current_section = ""
    current_title = ""

    for line in text.split('\n'):
        if line.startswith('#'):
            if current_title and current_section:
                sections.append({
                    "title": current_title,
                    "content": current_section.strip()
                })
            current_title = line.lstrip('#').strip()
            current_section = ""
        else:
            current_section += line + "\n"

    # Add the last section
    if current_title and current_section:
        sections.append({
            "title": current_title,
            "content": current_section.strip()
        })

    return sections

def format_references(references: List[Dict]) -> str:
    """Format references in a consistent way"""
    formatted_refs = "## References\n\n"
    for i, ref in enumerate(references, 1):
        formatted_refs += f"{i}. [{ref['title']}]({ref['url']}) - {ref['source']}\n"
    return formatted_refs

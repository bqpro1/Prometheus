"""
URL utilities for the Odysseus agent.
Contains functions for normalizing and processing URLs.
"""

from urllib.parse import urlparse, urlunparse
import re

def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing the fragment part (everything after #)
    and ensuring consistent formatting.
    """
    if not url:
        return url
        
    # Parse the URL
    parsed = urlparse(url)
    
    # Remove the fragment
    normalized = urlunparse((
        parsed.scheme, 
        parsed.netloc, 
        parsed.path,
        parsed.params,
        parsed.query,
        ''  # Empty fragment
    ))
    
    # Remove trailing period some links might have
    if normalized.endswith(')'):
        normalized = normalized[:-1]
        
    return normalized

def clean_url(url: str) -> str:
    """
    Clean a URL by removing common issues like trailing punctuation
    and adding a scheme if missing.
    """
    if not url:
        return url
        
    # Remove trailing punctuation that might be part of the text
    url = re.sub(r'[.,;:!?)\]}]+$', '', url)
    
    # Remove trailing parenthesis that might be captured in regex
    url = re.sub(r'\)+$', '', url)
    
    # Fix URL if missing scheme
    if not url.startswith('http'):
        url = 'https://' + url
        
    return url

def extract_urls_from_text(text: str) -> list:
    """
    Extract URLs from text using a robust regex pattern.
    Returns a list of cleaned URLs.
    """
    if not text:
        return []
        
    # Find URLs in the text
    urls = re.findall(r'https?://[^\s()<>"\'\[\]]+', text)
    
    # Clean up URLs
    cleaned_urls = []
    for url in urls:
        cleaned_urls.append(clean_url(url))
    
    return cleaned_urls 
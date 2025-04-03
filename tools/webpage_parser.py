from agents import FunctionTool
from typing import List, Dict, Any, Optional
import json
import requests
import tiktoken
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


class WebpageParserTool(FunctionTool):
    """Tool for parsing webpage content"""
    
    def __init__(self):
        """Initialize the webpage parser tool"""
        
        async def parse_webpage_impl(ctx, params_json):
            params = json.loads(params_json)
            url = params.get("url", "")
            
            """Extract the main content from a webpage URL"""
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title = soup.title.string if soup.title else "Untitled"
                
                # Extract main content (simplified)
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text
                text = soup.get_text(separator=' ')
                
                # Break into lines and remove leading/trailing space
                lines = (line.strip() for line in text.splitlines())
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # Remove blank lines
                content = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Limit token count
                encoder = tiktoken.get_encoding("cl100k_base")
                tokens = encoder.encode(content)
                if len(tokens) > 16000:
                    content = encoder.decode(tokens[:16000]) + "\n[Content truncated due to length...]"
                
                return {
                    "title": title,
                    "content": content,
                    "url": url
                }
            
            except Exception as e:
                # Return error message in content
                return {
                    "title": "Error Parsing Webpage",
                    "content": f"Failed to parse webpage: {str(e)}",
                    "url": url
                }
                
        # Create the parameter schema
        params_schema = {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to parse"
                }
            },
            "required": ["url"],
            "additionalProperties": False
        }
        
        super().__init__(
            name="parse_webpage",
            description="Extract the main content from a webpage URL",
            params_json_schema=params_schema,
            on_invoke_tool=parse_webpage_impl
        )


class WebpageExtractLinksTool(FunctionTool):
    """Tool for extracting links from a webpage"""
    
    def __init__(self):
        """Initialize the links extraction tool"""
        
        async def extract_webpage_links_impl(ctx, params_json):
            params = json.loads(params_json)
            url = params.get("url", "")
            
            """Extract all links from a webpage"""
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                links = []
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                        href = urljoin(base_url, href)
                    
                    # Only include http/https links
                    if href.startswith(('http://', 'https://')):
                        link_text = a_tag.get_text(strip=True) or "[No text]"
                        links.append({
                            "text": link_text,
                            "url": href
                        })
                
                # Limit to 100 links to avoid overwhelming the agent
                if len(links) > 100:
                    links = links[:100]
                
                return {
                    "links": links,
                    "url": url
                }
            
            except Exception as e:
                # Return empty links list on error
                return {
                    "links": [],
                    "url": url,
                    "error": str(e)
                }
                
        # Create the parameter schema
        params_schema = {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to extract links from"
                }
            },
            "required": ["url"],
            "additionalProperties": False
        }
        
        super().__init__(
            name="extract_webpage_links",
            description="Extract all links from a webpage",
            params_json_schema=params_schema,
            on_invoke_tool=extract_webpage_links_impl
        ) 
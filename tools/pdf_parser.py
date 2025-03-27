from agents import FunctionTool
from typing import List, Dict, Any, Optional
import json
import tempfile
import os
import requests
import tiktoken
from PyPDF2 import PdfReader
import re


class PDFParserTool(FunctionTool):
    """Tool for parsing PDF documents"""
    
    def __init__(self):
        """Initialize the PDF parser tool"""
        
        async def parse_pdf_impl(ctx, params_json):
            params = json.loads(params_json)
            url = params.get("url", "")
            
            """Extract text content from a PDF document"""
            try:
                # Download the PDF file to a temporary location
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                # Create a temporary file
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    temp_path = temp_file.name
                    # Write PDF content to the file
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            temp_file.write(chunk)
                
                try:
                    # Extract text from the PDF
                    reader = PdfReader(temp_path)
                    num_pages = len(reader.pages)
                    
                    # Extract text from each page
                    pages_content = []
                    for i in range(num_pages):
                        page = reader.pages[i]
                        text = page.extract_text()
                        if text:
                            # Clean up excessive whitespace
                            text = re.sub(r'\s+', ' ', text)
                            pages_content.append(text)
                    
                    # Join all pages
                    content = "\n\n".join(pages_content)
                    
                    # Try to extract title from the first page
                    title = "PDF Document"
                    if pages_content and len(pages_content) > 0:
                        # Simple heuristic: first line of first page might be title
                        first_lines = pages_content[0].strip().split('\n')
                        if first_lines and len(first_lines[0]) < 200:  # Title shouldn't be too long
                            title = first_lines[0]
                    
                    # Limit token count to avoid exceeding limits
                    encoder = tiktoken.get_encoding("cl100k_base")
                    tokens = encoder.encode(content)
                    if len(tokens) > 16000:
                        content = encoder.decode(tokens[:16000]) + "\n[Content truncated due to length...]"
                    
                    return {
                        "title": title,
                        "content": content,
                        "url": url,
                        "page_count": num_pages
                    }
                
                finally:
                    # Clean up the temporary file
                    os.unlink(temp_path)
            
            except Exception as e:
                # Return error information
                return {
                    "title": "Error Parsing PDF",
                    "content": f"Failed to parse PDF: {str(e)}",
                    "url": url,
                    "page_count": 0
                }
                
        # Create the parameter schema
        params_schema = {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the PDF to parse"
                }
            },
            "required": ["url"],
            "additionalProperties": False
        }
        
        super().__init__(
            name="parse_pdf",
            description="Extract text content from a PDF document",
            params_json_schema=params_schema,
            on_invoke_tool=parse_pdf_impl
        ) 
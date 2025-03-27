from agents import FunctionTool
from typing import List, Dict, Any, Optional
import json
import requests
import inspect
import asyncio


class BraveSearchTool(FunctionTool):
    """Tool for searching the web using Brave Search API"""
    
    def __init__(self, api_key: str):
        """Initialize the Brave Search tool with the API key"""
        self.api_key = api_key
        
        async def brave_search_impl(ctx, params_json):
            params = json.loads(params_json)
            query = params.get("query", "")
            count = params.get("count", 10)
            
            """
            Search the web using the Brave Search API
            """
            url = "https://api.search.brave.com/res/v1/web/search"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": min(count, 20),  # Limit to 20 max
            }
            
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("web", {}).get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("url", ""),
                        "snippet": item.get("description", "")
                    })
                
                return {"results": results}
            
            except Exception as e:
                # Return empty results on error but log the error
                print(f"Error in Brave Search: {str(e)}")
                return {"results": [], "error": str(e)}
        
        # Create the parameter schema
        params_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up on Brave Search"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results to return (1-20)"
                }
            },
            "required": ["query", "count"],
            "additionalProperties": False
        }
        
        # Initialize the FunctionTool
        super().__init__(
            name="brave_search",
            description="Search the web for information using Brave Search API",
            params_json_schema=params_schema,
            on_invoke_tool=brave_search_impl
        ) 
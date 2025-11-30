"""
Web Search Tool

This tool allows the AI agent to perform web searches using the official
Google Custom Search JSON API and scrape the content from the top search results.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from modules.config import GOOGLE_SEARCH_CONFIG

class WebSearchTool:
    """
    A tool to search Google and scrape content from the top results using the
    Google Custom Search JSON API.
    """
    
    def __init__(self):
        """
        Initialize the Web Search tool.
        """
        self.tool_name = "WEB_SEARCH"
        self.api_key = GOOGLE_SEARCH_CONFIG.get("api_key")
        self.search_engine_id = GOOGLE_SEARCH_CONFIG.get("search_engine_id")
        self.api_endpoint = "https://www.googleapis.com/customsearch/v1"

    def search_and_fetch_content(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Performs a Google search for the query and scrapes the text content
        from the top N results.

        Args:
            query: The search query.
            num_results: The number of top results to scrape (default: 3).

        Returns:
            A dictionary containing the scraped content from the search results.
        """
        # Check if API credentials are configured
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return {"success": False, "error": "Google API key is not configured in modules/config.py"}
        if not self.search_engine_id or self.search_engine_id == "YOUR_CX_ID":
            return {"success": False, "error": "Google Search Engine ID (CX ID) is not configured in modules/config.py"}
            
        try:
            # --- Perform the Google Custom Search ---
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results
            }
            response = requests.get(self.api_endpoint, params=params)
            response.raise_for_status()
            search_data = response.json()
            
            search_results_urls = [item['link'] for item in search_data.get('items', [])]
            
            if not search_results_urls:
                return {
                    "success": False,
                    "error": "No search results found."
                }
            
            # --- Scrape content from the URLs ---
            scraped_content = []
            for url in search_results_urls:
                try:
                    scrape_response = requests.get(url, timeout=10)
                    scrape_response.raise_for_status()
                    
                    soup = BeautifulSoup(scrape_response.content, 'html.parser')
                    for script_or_style in soup(["script", "style"]):
                        script_or_style.decompose()
                        
                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    scraped_content.append({
                        "url": url,
                        "content": text[:5000]
                    })
                except Exception as e:
                    scraped_content.append({
                        "url": url,
                        "error": f"Failed to scrape content: {str(e)}"
                    })
            
            return {
                "success": True,
                "results": scraped_content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An unexpected error occurred during the search: {str(e)}"
            }

    def get_tool_spec(self) -> Dict[str, Any]:
        """
        Get the tool specification for AI agent integration.
        """
        return {
            "tool_name": self.tool_name,
            "description": "Performs a web search using the Google Custom Search API and scrapes content from the top results. Useful for finding up-to-date information or learning about a new topic.",
            "methods": [
                {
                    "name": "search_and_fetch_content",
                    "description": "Searches a query on Google and returns the text content of the top search results.",
                    "parameters": {
                        "query": {
                            "type": "string",
                            "description": "The search query to look up.",
                            "required": True
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "The number of top search results to fetch content from (max 10).",
                            "required": False,
                            "default": 3
                        }
                    },
                    "returns": "A dictionary containing a list of results. Each result includes the source URL and the scraped text content (or an error message).",
                    "destruct_flag": False
                }
            ]
        }
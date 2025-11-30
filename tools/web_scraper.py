"""
Web Scraper Tool

This tool allows the AI agent to fetch the text content from a given URL.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

class WebScraperTool:
    """
    A tool to scrape the text content of a single web page.
    """
    
    def __init__(self):
        """
        Initialize the Web Scraper tool.
        """
        self.tool_name = "WEB_SCRAPER"

    def scrape(self, url: str) -> Dict[str, Any]:
        """
        Fetches the given URL and returns its cleaned text content.

        Args:
            url: The URL to scrape.

        Returns:
            A dictionary containing the URL and its text content, or an error.
        """
        try:
            # Fetch the content of the URL
            response = requests.get(url, timeout=15)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the HTML and extract text
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
                
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return {
                "success": True,
                "url": url,
                "content": text
            }
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"Failed to scrape content: {str(e)}"
            }

    def get_tool_spec(self) -> Dict[str, Any]:
        """
        Get the tool specification for AI agent integration.
        """
        return {
            "tool_name": self.tool_name,
            "description": "Fetches the text content of a single web page. Useful for reading articles, documentation, or other web content from a known URL.",
            "methods": [
                {
                    "name": "scrape",
                    "description": "Returns the cleaned text content for a given URL.",
                    "parameters": {
                        "url": {
                            "type": "string",
                            "description": "The full URL of the web page to scrape.",
                            "required": True
                        }
                    },
                    "returns": "A dictionary containing the URL and its text content, or an error message.",
                    "destruct_flag": False
                }
            ]
        }

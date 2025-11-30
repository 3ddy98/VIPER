"""
Unit tests for the WebSearchTool.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests
from tools.web_search import WebSearchTool

class TestWebSearchTool(unittest.TestCase):
    """
    Test suite for the WebSearchTool.
    
    These tests use mocking to prevent actual network requests to Google
    or other websites, ensuring that the tests are fast and reliable.
    """
    
    def setUp(self):
        """Set up a new WebSearchTool instance for each test."""
        self.tool = WebSearchTool()

    @patch('tools.web_search.search')
    @patch('tools.web_search.requests.get')
    def test_search_and_fetch_success(self, mock_requests_get, mock_google_search):
        """
        Test the successful case where search results are found and scraped.
        """
        # --- Arrange ---
        # Mock the Google search to return a list of fake URLs
        mock_google_search.return_value = [
            "http://fakeurl1.com",
            "http://fakeurl2.com"
        ]
        
        # Mock the response from requests.get
        mock_response1 = MagicMock()
        mock_response1.content = b"<html><body><h1>Title 1</h1><p>Content 1</p></body></html>"
        mock_response1.raise_for_status = MagicMock()

        mock_response2 = MagicMock()
        mock_response2.content = b"<html><body><h2>Title 2</h2><div>Content 2</div></body></html>"
        mock_response2.raise_for_status = MagicMock()

        # Set the side_effect to return different responses for each call
        mock_requests_get.side_effect = [mock_response1, mock_response2]

        # --- Act ---
        result = self.tool.search_and_fetch_content("test query", num_results=2)

        # --- Assert ---
        self.assertTrue(result["success"])
        self.assertEqual(len(result["results"]), 2)
        
        # Check first result
        self.assertEqual(result["results"][0]["url"], "http://fakeurl1.com")
        self.assertIn("Title 1", result["results"][0]["content"])
        self.assertIn("Content 1", result["results"][0]["content"])
        
        # Check second result
        self.assertEqual(result["results"][1]["url"], "http://fakeurl2.com")
        self.assertIn("Title 2", result["results"][1]["content"])
        self.assertIn("Content 2", result["results"][1]["content"])

    @patch('tools.web_search.search')
    def test_search_no_results(self, mock_google_search):
        """
        Test the case where the Google search returns no results.
        """
        # --- Arrange ---
        mock_google_search.return_value = []

        # --- Act ---
        result = self.tool.search_and_fetch_content("a query with no results")

        # --- Assert ---
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "No search results found.")

    @patch('tools.web_search.search')
    @patch('tools.web_search.requests.get')
    def test_search_one_url_fails(self, mock_requests_get, mock_google_search):
        """
        Test the case where one of the URLs fails to scrape.
        """
        # --- Arrange ---
        mock_google_search.return_value = ["http://goodurl.com", "http://badurl.com"]
        
        # Mock a successful response
        mock_good_response = MagicMock()
        mock_good_response.content = b"<html><body>Good content</body></html>"
        mock_good_response.raise_for_status = MagicMock()
        
        # Mock a failed response (requests.get will raise an exception)
        mock_requests_get.side_effect = [
            mock_good_response,
            requests.exceptions.RequestException("Failed to connect")
        ]

        # --- Act ---
        result = self.tool.search_and_fetch_content("test query")

        # --- Assert ---
        self.assertTrue(result["success"])
        self.assertEqual(len(result["results"]), 2)
        
        # Check the successful result
        self.assertEqual(result["results"][0]["url"], "http://goodurl.com")
        self.assertIn("Good content", result["results"][0]["content"])
        self.assertNotIn("error", result["results"][0])
        
        # Check the failed result
        self.assertEqual(result["results"][1]["url"], "http://badurl.com")
        self.assertIn("error", result["results"][1])
        self.assertIn("Failed to scrape content", result["results"][1]["error"])

    @patch('tools.web_search.search')
    def test_best_enchilada_recipe_no_results(self, mock_google_search):
        """
        Test the scenario where the tool is queried for "best enchilada recipe"
        but the underlying search function returns no results.
        """
        # --- Arrange ---
        # Simulate googlesearch.search returning no results for the specific query
        mock_google_search.return_value = []

        # --- Act ---
        result = self.tool.search_and_fetch_content("best enchilada recipe", num_results=3)

        # --- Assert ---
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "No search results found.")
# src/retrieval.py
import requests
from typing import List, Dict, Any
from datetime import datetime
import logging

class GoogleRetrieval:
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a Google Custom Search and return formatted results.
        """
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': min(num_results, 10),  # Google CSE max is 10 per request
        }

        try:
            response = requests.get(self.base_url, params=params)

            # Print debugging information
            logging.info(f"Request URL: {response.url}")
            logging.info(f"Response Status: {response.status_code}")

            if response.status_code != 200:
                logging.error(f"Error Response: {response.text}")
                raise Exception(f"Google API returned status code {response.status_code}: {response.text}")

            data = response.json()

            # Check if we have search results
            if 'items' not in data:
                logging.warning("No search results found")
                return []

            results = []
            for item in data['items']:
                result = {
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': item.get('displayLink', ''),
                    'published_date': ''  # Initialize empty as it's not always available
                }

                # Try to get the publication date from metatags if available
                try:
                    metatags = item.get('pagemap', {}).get('metatags', [{}])[0]
                    result['published_date'] = (
                        metatags.get('article:published_time') or
                        metatags.get('datePublished') or
                        ''
                    )
                except (IndexError, KeyError):
                    pass

                results.append(result)

            return results

        except requests.exceptions.RequestException as e:
            logging.error(f"Request Exception: {str(e)}")
            raise Exception(f"Error accessing Google API: {str(e)}")
        except Exception as e:
            logging.error(f"General Exception: {str(e)}")
            raise Exception(f"Error processing search results: {str(e)}")

    def format_results_for_prompt(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a structured string for the LLM prompt.
        """
        if not results:
            return "No search results found. Please try a different query or check the search configuration."

        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"""[{i}] {result['title']}
Source: {result['source']}
URL: {result['url']}
Summary: {result['snippet']}"""

            if result['published_date']:
                formatted_result += f"\nPublished: {result['published_date']}"

            formatted_results.append(formatted_result)

        return "\n\n".join(formatted_results)

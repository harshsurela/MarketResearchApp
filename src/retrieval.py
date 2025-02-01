import requests
from typing import List, Dict, Any
from datetime import datetime
import logging
import time
import streamlit as st
import asyncio
from concurrent.futures import ThreadPoolExecutor

class GoogleRetrieval:
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.last_request_time = datetime.now()
        self.request_delay = 1
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def gather_research_data(self, topic: str, sections: Dict) -> Dict[str, List[Dict]]:
        """Gather research data for all sections in parallel"""
        tasks = []
        for section_name in sections:
            # Create search query for each section
            search_query = self._create_section_query(topic, section_name)
            tasks.append(self._async_search(search_query, section_name))

        # Gather all results
        results = await asyncio.gather(*tasks)
        return {section: result for section, result in results}

    async def _async_search(self, query: str, section_name: str) -> tuple:
        """Perform async search for a section"""
        try:
            results = await self.search(query, num_results=5)
            return (section_name, results)
        except Exception as e:
            logging.error(f"Search error for {section_name}: {str(e)}")
            return (section_name, [])

    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Perform Google Custom Search with enhanced error handling"""
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': min(num_results, 10),
            'dateRestrict': 'y2',  # Last 2 years
            'sort': 'date'
        }

        try:
            # Rate limiting
            await self._handle_rate_limit()

            # Make async request
            response = await self._async_get(params)

            if response.status_code != 200:
                logging.error(f"Search API error: {response.status_code} - {response.text}")
                return self._get_default_results(query)

            data = response.json()

            if 'items' not in data:
                logging.warning(f"No results found for: {query}")
                return self._get_default_results(query)

            return self._process_search_results(data['items'])

        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            return self._get_default_results(query)

    async def _async_get(self, params: Dict) -> requests.Response:
        """Make async HTTP GET request"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
        )

    async def _handle_rate_limit(self):
        """Handle rate limiting"""
        time_since_last_request = (datetime.now() - self.last_request_time).total_seconds()
        if time_since_last_request < self.request_delay:
            await asyncio.sleep(self.request_delay - time_since_last_request)
        self.last_request_time = datetime.now()

    def _process_search_results(self, items: List[Dict]) -> List[Dict]:
        """Process and format search results"""
        processed_results = []
        for item in items:
            result = {
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': item.get('displayLink', ''),
                'published_date': self._extract_date(item),
                'metadata': self._extract_metadata(item)
            }
            processed_results.append(result)
        return processed_results

    def _extract_date(self, item: Dict) -> str:
        """Extract publication date from search result"""
        try:
            metatags = item.get('pagemap', {}).get('metatags', [{}])[0]
            date = (
                metatags.get('article:published_time') or
                metatags.get('datePublished') or
                metatags.get('og:updated_time') or
                datetime.now().strftime('%Y-%m-%d')
            )
            return date
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')

    def _extract_metadata(self, item: Dict) -> Dict:
        """Extract additional metadata from search result"""
        try:
            metatags = item.get('pagemap', {}).get('metatags', [{}])[0]
            return {
                'description': metatags.get('og:description', ''),
                'site_name': metatags.get('og:site_name', ''),
                'type': metatags.get('og:type', ''),
                'author': metatags.get('author', '')
            }
        except Exception:
            return {}

    def _create_section_query(self, topic: str, section_name: str) -> str:
        """Create optimized search query for section"""
        section_keywords = {
            "Executive Summary": "market overview summary statistics",
            "Industry Overview": "industry analysis market size revenue",
            "Market Analysis": "market trends analysis data statistics",
            "Competitive Landscape": "market share competitors analysis",
            "Technology and Innovation": "technology trends innovation development",
            # Add keywords for other sections...
        }

        base_query = f"{topic} {section_keywords.get(section_name, '')}"
        return f"{base_query} market research report analysis"

    def _get_default_results(self, query: str) -> List[Dict[str, Any]]:
        """Provide default results when search fails"""
        return [{
            'title': f"Market Research: {query}",
            'url': "https://example.com",
            'snippet': (
                f"Comprehensive market research data for {query}. "
                "The search service is currently unavailable, but we can still "
                "provide analysis based on general market knowledge."
            ),
            'source': "Market Research Database",
            'published_date': datetime.now().strftime('%Y-%m-%d'),
            'metadata': {
                'description': f"Market research information about {query}",
                'site_name': "Market Research Database",
                'type': "article",
                'author': "Market Research Team"
            }
        }]

    def format_results_for_prompt(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM prompt"""
        if not results:
            return "No specific research data available. Proceeding with general market knowledge."

        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"""
            [Source {i}]
            Title: {result['title']}
            Source: {result['source']}
            Date: {result['published_date']}
            Key Information: {result['snippet']}
            URL: {result['url']}
            Additional Details: {result['metadata'].get('description', '')}
            ---"""
            formatted_results.append(formatted_result)

        return "\n\n".join(formatted_results)

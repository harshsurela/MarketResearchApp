import requests
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import re
import logging
import io
import base64

class ChartGenerator:
    def __init__(self):
        self.setup_style()

    def setup_style(self):
        """Setup matplotlib style"""
        try:
            # Use a basic style instead of seaborn
            plt.style.use('bmh')  # This is a built-in style that's always available

            # Set custom style parameters
            plt.rcParams.update({
                'figure.figsize': [10, 6],
                'figure.dpi': 100,
                'font.size': 10,
                'axes.titlesize': 12,
                'axes.labelsize': 10,
                'axes.grid': True,
                'grid.alpha': 0.3,
                'axes.spines.top': False,
                'axes.spines.right': False,
                'lines.linewidth': 2,
                'lines.markersize': 8,
                'xtick.direction': 'out',
                'ytick.direction': 'out',
                'axes.prop_cycle': plt.cycler(color=[
                    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
                ])
            })

            # Set seaborn style if available
            try:
                sns.set_theme(style="whitegrid")
                sns.set_palette("husl")
            except Exception as e:
                logging.warning(f"Seaborn styling not available: {str(e)}")

        except Exception as e:
            logging.error(f"Error setting up chart style: {str(e)}")
            # Set minimal default style
            plt.rcParams.update({
                'figure.figsize': [10, 6],
                'figure.dpi': 100
            })
    def figure_to_base64(self, fig: plt.Figure) -> str:
            """Convert matplotlib figure to base64 string"""
            try:
                # Save figure to a temporary buffer.
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
                buf.seek(0)

                # Encode the bytes as base64
                image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                buf.close()

                return f"data:image/png;base64,{image_base64}"
            except Exception as e:
                logging.error(f"Error converting figure to base64: {str(e)}")
                return ""

    async def generate_charts(self, topic: str, section_name: str, content: str) -> List[str]:
            """Generate charts and return as base64 strings"""
            try:
                # Extract numerical data from content
                data = self.extract_data(content)
                if not data:
                    return []

                chart_figures = []
                if section_name == "Market Analysis":
                    chart_figures.extend(self._generate_market_charts(data, topic))
                elif section_name == "Competitive Landscape":
                    chart_figures.extend(self._generate_competitive_charts(data, topic))
                elif section_name == "Financial Analysis":
                    chart_figures.extend(self._generate_financial_charts(data, topic))
                elif section_name == "Implementation Roadmap":
                    chart_figures.extend(self._generate_roadmap_charts(data, topic))

                # Convert figures to base64 strings
                base64_charts = []
                for fig in chart_figures:
                    base64_str = self.figure_to_base64(fig)
                    if base64_str:
                        base64_charts.append(base64_str)
                    plt.close(fig)  # Clean up the figure

                return base64_charts

            except Exception as e:
                logging.error(f"Chart generation error for {section_name}: {str(e)}")
                return []

    def extract_data(self, content: str) -> Dict[str, Any]:
        """Extract numerical and textual data from content"""
        data = {
            'numbers': [],
            'percentages': [],
            'years': [],
            'companies': [],
            'market_shares': [],
            'trends': [],
            'categories': []
        }

        try:
            # Extract numbers and percentages
            data['numbers'] = [float(x) for x in re.findall(r'\b\d+\.?\d*\b(?!%)', content)]
            data['percentages'] = [float(x) for x in re.findall(r'(\d+\.?\d*)%', content)]

            # Extract years
            data['years'] = re.findall(r'\b20\d{2}\b', content)

            # Extract company names (assumed to be capitalized words)
            data['companies'] = re.findall(r'\b[A-Z][a-zA-Z\s]+(?=\s+(?:Company|Inc\.|Ltd\.|Corporation|Corp\.))', content)

            # Extract market shares
            market_shares = re.findall(r'(\w+(?:\s+\w+)*)\s*:\s*(\d+\.?\d*)%', content)
            if market_shares:
                data['market_shares'] = market_shares

            return data

        except Exception as e:
            logging.error(f"Data extraction error: {str(e)}")
            return data

    def _generate_market_charts(self, data: Dict[str, Any], topic: str) -> List[plt.Figure]:
        """Generate market analysis charts"""
        charts = []

        try:
            if data['numbers'] and data['years']:
                fig, ax = plt.subplots()
                years = data['years'][:5]  # Take first 5 years
                values = data['numbers'][:5]  # Take corresponding values

                ax.plot(years, values, marker='o', linewidth=2, markersize=8)
                ax.set_title(f'{topic} Market Growth Trend')
                ax.set_xlabel('Year')
                ax.set_ylabel('Market Size')
                plt.xticks(rotation=45)
                plt.tight_layout()
                charts.append(fig)
                plt.close(fig)

        except Exception as e:
            logging.error(f"Error generating market charts: {str(e)}")

        return charts

    def _generate_competitive_charts(self, data: Dict[str, Any], topic: str) -> List[plt.Figure]:
        """Generate competitive analysis charts"""
        charts = []

        try:
            if data['market_shares']:
                fig, ax = plt.subplots()
                companies, shares = zip(*data['market_shares'])
                shares = [float(share) for share in shares]

                plt.pie(shares, labels=companies, autopct='%1.1f%%')
                plt.title(f'{topic} Market Share Distribution')
                plt.tight_layout()
                charts.append(fig)
                plt.close(fig)

        except Exception as e:
            logging.error(f"Error generating competitive charts: {str(e)}")

        return charts

    def _generate_financial_charts(self, data: Dict[str, Any], topic: str) -> List[plt.Figure]:
        """Generate financial analysis charts"""
        charts = []

        try:
            if data['numbers']:
                fig, ax = plt.subplots()
                metrics = ['Revenue', 'Growth', 'Profit', 'Investment'][:len(data['numbers'])]
                values = data['numbers'][:len(metrics)]

                ax.bar(metrics, values)
                ax.set_title(f'{topic} Financial Metrics')
                plt.xticks(rotation=45)
                plt.tight_layout()
                charts.append(fig)
                plt.close(fig)

        except Exception as e:
            logging.error(f"Error generating financial charts: {str(e)}")

        return charts

    def _generate_roadmap_charts(self, data: Dict[str, Any], topic: str) -> List[plt.Figure]:
        """Generate implementation roadmap charts"""
        charts = []

        try:
            if data['years']:
                fig, ax = plt.subplots(figsize=(12, 6))
                phases = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4'][:len(data['years'])]
                years = data['years'][:len(phases)]

                # Create timeline
                ax.plot(years, range(len(years)), 'o-', linewidth=2, markersize=10)

                # Add labels
                for i, (year, phase) in enumerate(zip(years, phases)):
                    ax.annotate(f'{phase}\n{year}',
                              (year, i),
                              xytext=(10, 10),
                              textcoords='offset points')

                ax.set_title(f'{topic} Implementation Timeline')
                ax.set_xlabel('Year')
                ax.set_yticks([])
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                charts.append(fig)
                plt.close(fig)

        except Exception as e:
            logging.error(f"Error generating roadmap charts: {str(e)}")

        return charts
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

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import re
import logging

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

    async def generate_charts(self, topic: str, section_name: str, content: str) -> List[plt.Figure]:
        """Generate charts for a section"""
        try:
            # Extract numerical data from content
            data = self.extract_data(content)
            if not data:
                return []

            charts = []
            if section_name == "Market Analysis":
                charts.extend(self._generate_market_charts(data, topic))
            elif section_name == "Competitive Landscape":
                charts.extend(self._generate_competitive_charts(data, topic))
            elif section_name == "Financial Analysis":
                charts.extend(self._generate_financial_charts(data, topic))
            elif section_name == "Implementation Roadmap":
                charts.extend(self._generate_roadmap_charts(data, topic))

            return charts

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

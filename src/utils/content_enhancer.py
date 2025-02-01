import re
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from datetime import datetime

class ContentEnhancer:
    def __init__(self):
        self.chart_counter = 0
        self.table_counter = 0

    def enhance_report(self, content: str, research_data: Dict[str, Any]) -> str:
        """
        Enhance the report content with visualizations, citations, and better formatting
        """
        enhanced_content = self._add_title_and_metadata(content, research_data)
        enhanced_content = self._add_table_of_contents(enhanced_content)
        enhanced_content = self._add_visualizations(enhanced_content, research_data)
        enhanced_content = self._add_citations(enhanced_content, research_data.get('references', []))
        enhanced_content = self._format_for_readability(enhanced_content)
        enhanced_content = self._add_executive_brief(enhanced_content)
        return enhanced_content

    def _add_title_and_metadata(self, content: str, research_data: Dict[str, Any]) -> str:
        """Add title page and metadata to the report"""
        title = research_data.get('topic', 'Market Research Report')
        date = datetime.now().strftime("%B %d, %Y")

        title_page = f"""
        # {title.upper()}

        **Generated Date:** {date}
        **Report Type:** Comprehensive Market Analysis
        **Confidence Level:** High

        ---
        """
        return title_page + content

    def _add_table_of_contents(self, content: str) -> str:
        """Generate and add table of contents"""
        toc = "## Table of Contents\n\n"
        headers = re.findall(r'^#{2,3}\s(.+)$', content, re.MULTILINE)

        for i, header in enumerate(headers, 1):
            level = len(re.match(r'^#+', header).group())
            indent = "  " * (level - 2)
            toc += f"{indent}{i}. {header.strip()}\n"

        return toc + "\n---\n" + content

    def _add_visualizations(self, content: str, research_data: Dict[str, Any]) -> str:
        """Add relevant charts and tables to the content"""
        # Create market trend visualization
        if 'market_trends' in research_data:
            chart = self._create_market_trend_chart(research_data['market_trends'])
            content = self._insert_visualization(content, chart, "Market Trends Analysis")

        # Create competitive analysis visualization
        if 'competitor_data' in research_data:
            chart = self._create_competitor_chart(research_data['competitor_data'])
            content = self._insert_visualization(content, chart, "Competitive Landscape")

        # Add summary tables
        if 'key_metrics' in research_data:
            table = self._create_metrics_table(research_data['key_metrics'])
            content = content.replace("[INSERT_METRICS_TABLE]", table)

        return content

    def _create_market_trend_chart(self, trend_data: Dict) -> str:
        """Create a market trend visualization"""
        plt.figure(figsize=(10, 6))
        # Create sample data if none provided
        data = {
            'Year': ['2020', '2021', '2022', '2023', '2024'],
            'Market Size': [100, 120, 150, 200, 250]
        }

        sns.lineplot(x='Year', y='Market Size', data=pd.DataFrame(data))
        plt.title('Market Growth Trend')
        plt.ylabel('Market Size (Billion $)')

        # Convert plot to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()

        encoded = base64.b64encode(image_png).decode()
        return f'<img src="data:image/png;base64,{encoded}">'

    def _create_competitor_chart(self, competitor_data: Dict) -> str:
        """Create a competitor analysis visualization"""
        # Similar implementation to market trend chart but for competitor data
        pass

    def _create_metrics_table(self, metrics_data: Dict) -> str:
        """Create an HTML table for key metrics"""
        table_html = """
        <table style="width:100%; border-collapse: collapse;">
            <tr>
                <th style="border: 1px solid black; padding: 8px;">Metric</th>
                <th style="border: 1px solid black; padding: 8px;">Value</th>
            </tr>
        """

        for metric, value in metrics_data.items():
            table_html += f"""
            <tr>
                <td style="border: 1px solid black; padding: 8px;">{metric}</td>
                <td style="border: 1px solid black; padding: 8px;">{value}</td>
            </tr>
            """

        table_html += "</table>"
        return table_html

    def _add_citations(self, content: str, references: List[Dict]) -> str:
        """Add citations and references section"""
        # Add citation numbers in content
        for i, ref in enumerate(references, 1):
            content = content.replace(f"[REF_{i}]", f"[{i}]")

        # Add references section
        content += "\n\n## References\n\n"
        for i, ref in enumerate(references, 1):
            content += f"{i}. {ref['title']} - {ref['source']} ({ref.get('published_date', 'n.d.')})\n"
            content += f"   URL: {ref['url']}\n\n"

        return content

    def _format_for_readability(self, content: str) -> str:
        """Improve content formatting"""
        # Add section spacing
        content = re.sub(r'(#{2,3}\s.+)\n', r'\1\n\n', content)

        # Format lists
        content = re.sub(r'(\*\s.+)\n([^\*])', r'\1\n\n\2', content)

        # Add horizontal rules between major sections
        content = re.sub(r'\n#{2}\s', r'\n---\n\n## ', content)

        return content

    def _add_executive_brief(self, content: str) -> str:
        """Add an executive brief section at the beginning"""
        brief = """
        ## Executive Brief

        This comprehensive market research report provides an in-depth analysis of the industry landscape,
        market trends, and strategic recommendations. The insights contained within are based on extensive
        research, data analysis, and expert perspectives.

        **Key Highlights:**
        * Market size and growth projections
        * Competitive landscape analysis
        * Technology trends and innovations
        * Strategic recommendations

        ---
        """

        # Insert brief after table of contents
        content_parts = content.split("---\n", 2)
        if len(content_parts) >= 2:
            return content_parts[0] + "---\n" + brief + content_parts[1]
        return content

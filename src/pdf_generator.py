import pdfkit
from datetime import datetime
import logging
from typing import Dict, Any
import os
import streamlit as st

class PDFGenerator:
    def __init__(self):
        self.options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }

    def generate_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """Generate PDF from report data"""
        try:
            html_content = self._create_html_content(report_data)
            return pdfkit.from_string(html_content, False, options=self.options)
        except Exception as e:
            logging.error(f"PDF generation error: {str(e)}")
            raise

    def _create_html_content(self, report_data: Dict[str, Any]) -> str:
        """Create HTML content from report data"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
                h2 {{ color: #34495e; margin-top: 30px; border-bottom: 2px solid #eee; }}
                .date {{ text-align: center; color: #666; margin-bottom: 40px; }}
                .section {{ margin-bottom: 30px; }}
                .content {{ text-align: justify; }}
                .page-break {{ page-break-after: always; }}
            </style>
        </head>
        <body>
            <h1>{report_data['topic']}</h1>
            <div class="date">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        """

        # Add table of contents
        html += "<h2>Table of Contents</h2><ul>"
        for section_name in report_data['content'].keys():
            html += f"<li>{section_name}</li>"
        html += "</ul><div class='page-break'></div>"

        # Add content sections
        for section_name, content in report_data['content'].items():
            html += f"""
            <div class='section'>
                <h2>{section_name}</h2>
                <div class='content'>{content}</div>
            </div>
            <div class='page-break'></div>
            """

        html += "</body></html>"
        return html

import pdfkit
from datetime import datetime
import logging
from typing import Dict, Any
import base64
import re

class PDFGenerator:
    def __init__(self):
        self.options = {
            'page-size': 'A4',
            'margin-top': '25mm',
            'margin-right': '20mm',
            'margin-bottom': '25mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
            'footer-right': '[page] of [topage]',
            'footer-font-size': '9',
            'footer-spacing': '5',
            'header-spacing': '5',
            'title': 'Market Research Report',
            'disable-smart-shrinking': None
        }

        # Logo as inline SVG converted to base64
        self.logo_base64 = """
        PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0i
        NTAiPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iZ3JhZCIgeDE9IjAlIiB5MT0iMCUiIHgyPSIxMDAl
        IiB5Mj0iMTAwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3R5bGU9InN0b3AtY29sb3I6IzFhMzY1ZDtzdG9w
        LW9wYWNpdHk6MSIgLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiMyRDM3NDg7
        c3RvcC1vcGFjaXR5OjEiIC8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHRleHQgeD0iMTAiIHk9IjM1
        IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMzAiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxs
        PSJ1cmwoI2dyYWQpIj5GaWZ0eUNvcmU8L3RleHQ+PC9zdmc+
        """

    def _create_header_html(self) -> str:
        """Create header HTML with FiftyCore branding"""
        return f"""
        <div style="text-align: right; padding: 10px;">
            <div style="font-family: 'Inter', Arial, sans-serif;
                        font-size: 24px;
                        font-weight: bold;
                        background: linear-gradient(135deg, #1a365d 0%, #2D3748 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        display: inline-block;">
                FiftyCore
                <span style="font-size: 12px;
                           display: block;
                           text-align: right;
                           margin-top: -5px;
                           color: #4A5568;
                           -webkit-text-fill-color: #4A5568;">
                    Market Intelligence
                </span>
            </div>
        </div>
        """

    def _create_watermark(self) -> str:
        """Create watermark for pages"""
        return """
        <div style="position: fixed;
                    bottom: 10px;
                    right: 10px;
                    opacity: 0.1;
                    transform: rotate(-45deg);
                    font-size: 60px;
                    color: #1a365d;">
            FiftyCore
        </div>
        """

    def _process_content(self, content: str) -> str:
        """
        Process model-generated content to convert markdown to HTML with proper formatting.
        Enhanced to better handle markdown from model output.
        """
        # Handle nested formatting by processing from inside out
        def process_nested(text: str) -> str:
            # Process inline code first (if present in model output)
            text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)

            # Process bold and italic together to handle nested cases
            text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)

            return text

        # Split content into lines for processing
        lines = content.split('\n')
        processed_lines = []
        in_list = False
        list_buffer = []

        for line in lines:
            # Process headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                header_content = process_nested(header_match.group(2))
                processed_lines.append(f'<h{level}>{header_content}</h{level}>')
                continue

            # Process lists
            list_match = re.match(r'^(\s*[-*]|\d+\.)\s+(.+)$', line)
            if list_match:
                if not in_list:
                    in_list = True
                    list_buffer = []
                item_content = process_nested(list_match.group(2))
                list_buffer.append(f'<li>{item_content}</li>')
            else:
                if in_list:
                    # Close list
                    list_html = '<ul>' + ''.join(list_buffer) + '</ul>'
                    processed_lines.append(list_html)
                    in_list = False
                    list_buffer = []

                # Process regular paragraph content
                if line.strip():
                    processed_line = process_nested(line)
                    processed_lines.append(f'<p>{processed_line}</p>')
                else:
                    processed_lines.append('<br>')

        # Close any remaining list
        if in_list:
            list_html = '<ul>' + ''.join(list_buffer) + '</ul>'
            processed_lines.append(list_html)

        return '\n'.join(processed_lines)

    def _create_html_content(self, report_data: Dict[str, Any]) -> str:
        """Create HTML content with modern design"""
        # Process each section's content
        processed_content = {}
        for section_name, content in report_data['content'].items():
            processed_content[section_name] = self._process_content(content)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

                body {{
                    font-family: 'Inter', sans-serif;
                    line-height: 1.6;
                    color: #2D3748;
                    margin: 0;
                    padding: 0;
                }}

                .cover-page {{
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    background: linear-gradient(135deg, #1a365d 0%, #2D3748 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                    position: relative;
                }}

                .logo-container {{
                    position: absolute;
                    top: 40px;
                    left: 40px;
                    font-size: 36px;
                    font-weight: bold;
                    color: rgba(255, 255, 255, 0.9);
                }}

                .content-section h1, h2, h3, h4, h5, h6 {{
                    color: #1a365d;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }}

                strong {{
                    color: #2D3748;
                    font-weight: 600;
                }}

                em {{
                    color: #4A5568;
                }}

                ul, ol {{
                    margin: 1em 0;
                    padding-left: 2em;
                }}

                li {{
                    margin: 0.5em 0;
                }}

                p {{
                    margin: 1em 0;
                }}

                {self._get_content_styles()}
            </style>
        </head>
        <body>
            <!-- Cover Page -->
            <div class="cover-page">
                <div class="logo-container">
                    FiftyCore
                    <div class="logo-subtitle">Market Intelligence</div>
                </div>
                <h1>{report_data['topic']}</h1>
                <div class="subtitle">Market Research Report</div>
                <div class="date">Generated on {datetime.now().strftime('%B %d, %Y')}</div>
            </div>
            <div class="page-break"></div>

            <!-- Table of Contents -->
            <div class="toc">
                <h2>Table of Contents</h2>
                <ul>
                    {''.join(f"<li>{section_name}</li>" for section_name in report_data['content'].keys())}
                </ul>
            </div>
            <div class="page-break"></div>

            <!-- Content Sections -->
            {''.join(
                f"""
                <div class="content-section">
                    {self._create_watermark()}
                    <h2>{section_name}</h2>
                    <div class="content">
                        {content}
                    </div>
                </div>
                <div class="page-break"></div>
                """
                for section_name, content in processed_content.items()
            )}

            <div class="footer">
                <p>© 2024 FiftyCore AI. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        return html

    def _get_content_styles(self) -> str:
        """Get CSS styles for content sections"""
        return """
            .content-section {
                margin-top: 40px;
                position: relative;
            }

            h2 {
                color: #1a365d;
                font-size: 24px;
                font-weight: 600;
                margin-top: 40px;
                margin-bottom: 20px;
                border-bottom: 2px solid #E2E8F0;
                padding-bottom: 10px;
            }

            .toc {
                margin: 40px 0;
                padding: 20px;
                background: #F7FAFC;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            .toc h2 {
                color: #1a365d;
                border-bottom: none;
                margin-top: 0;
            }

            .toc ul {
                list-style-type: none;
                padding-left: 0;
            }

            .toc li {
                margin: 10px 0;
                color: #4A5568;
                padding-left: 20px;
                position: relative;
            }

            .toc li:before {
                content: "•";
                color: #1a365d;
                position: absolute;
                left: 0;
            }

            .content {
                text-align: justify;
                margin-bottom: 20px;
            }

            .footer {
                text-align: center;
                font-size: 12px;
                color: #718096;
                margin-top: 40px;
                border-top: 1px solid #E2E8F0;
                padding-top: 20px;
            }
        """

    def generate_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """Generate PDF from report data"""
        try:
            html_content = self._create_html_content(report_data)
            return pdfkit.from_string(html_content, False, options=self.options)
        except Exception as e:
            logging.error(f"PDF generation error: {str(e)}")
            raise

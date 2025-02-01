import streamlit as st
import time
from datetime import datetime
import json
import os
import asyncio
import logging
from typing import Callable, Dict, Any
from src.generator import ReportGenerator
from src.llm import GroqLLM
from src.retrieval import GoogleRetrieval
from src.pdf_generator import PDFGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Market Research Report Generator",
    page_icon="📊",
    layout="wide"
)

async def generate_report_async(topic: str, progress_callback: Callable) -> Dict[str, Any]:
    """Generate report asynchronously with proper error handling"""
    try:
        # Get API keys from secrets
        api_keys = []
        for i in range(1, 6):  # Try to get up to 5 API keys
            key = st.secrets.get(f"GROQ_API_KEY_{i}")
            if key and key.strip():
                api_keys.append(key.strip())

        if not api_keys:
            raise ValueError("No API keys found in secrets")

        logger.info(f"Initialized with {len(api_keys)} API keys")

        # Initialize components
        llm = GroqLLM(api_keys=api_keys)
        retriever = GoogleRetrieval(
            st.secrets["GOOGLE_API_KEY"],
            st.secrets["GOOGLE_CSE_ID"]
        )

        # Create generator
        generator = ReportGenerator(llm, retriever)

        # Generate report
        return await generator.generate_full_report(topic, progress_callback)

    except Exception as e:
        logger.error(f"Error in report generation: {str(e)}")
        raise

def save_report(report_data: Dict[str, Any], format: str = 'json') -> str:
    """Save report to file system"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{timestamp}_{report_data['topic'].replace(' ', '_')}"

        os.makedirs("reports", exist_ok=True)

        if format == 'json':
            filename = f"reports/{base_filename}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)
        elif format == 'pdf':
            filename = f"reports/{base_filename}.pdf"
            pdf_generator = PDFGenerator()
            pdf_content = pdf_generator.generate_pdf(report_data)
            with open(filename, 'wb') as f:
                f.write(pdf_content)

        logger.info(f"Report saved to {filename}")
        return filename

    except Exception as e:
        logger.error(f"Error saving report: {str(e)}")
        raise

def display_report_content(report_data: Dict[str, Any]):
    """Display report content in a structured way"""
    st.title(report_data['topic'])
    st.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Display table of contents
    st.header("Table of Contents")
    for section_name in report_data['content'].keys():
        st.write(f"- {section_name}")

    # Display each section
    for section_name, content in report_data['content'].items():
        with st.expander(f"📄 {section_name}", expanded=True):
            st.markdown(content)

def generate_report_page():
    """Main report generation page"""
    st.title("🎯 Market Research Report Generator")

    # Add description
    st.write("""
    Generate comprehensive market research reports with AI assistance.
    The report will be approximately 15 pages long and include detailed analysis,
    charts, and citations.
    """)

    # Input section
    topic = st.text_input(
        "Research Topic",
        help="Enter the topic for your market research report",
        placeholder="e.g., Electric Vehicle Market in Europe"
    )

    if st.button("🚀 Generate Report", disabled=not topic, type="primary"):
        try:
            with st.spinner("Initializing report generation..."):
                # Progress tracking
                progress_container = st.container()
                progress_bar = progress_container.progress(0)
                status_text = progress_container.empty()

                def update_progress(status: str, progress: float):
                    status_text.text(f"Status: {status}")
                    progress_bar.progress(progress)
                    logger.info(f"Progress: {status} - {progress:.2%}")

                # Generate report
                report_data = asyncio.run(
                    generate_report_async(topic, update_progress)
                )

                # Save reports
                json_filename = save_report(report_data, 'json')
                pdf_filename = save_report(report_data, 'pdf')

                # Show success message
                st.success("✅ Report generated successfully!")

                # Display content
                st.header("📑 Report Preview")
                display_report_content(report_data)

                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    with open(json_filename, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="📥 Download JSON Report",
                            data=f.read(),
                            file_name=f"{topic.replace(' ', '_')}_report.json",
                            mime="application/json"
                        )

                with col2:
                    with open(pdf_filename, 'rb') as f:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=f.read(),
                            file_name=f"{topic.replace(' ', '_')}_report.pdf",
                            mime="application/pdf"
                        )

        except Exception as e:
            st.error("❌ Failed to generate report")
            st.error(f"Error details: {str(e)}")
            logger.error(f"Report generation failed: {str(e)}", exc_info=True)

            with st.expander("Show detailed error information"):
                st.code(str(e))

if __name__ == "__main__":
    try:
        generate_report_page()
    except Exception as e:
        st.error("Application error occurred")
        logger.error("Application error", exc_info=True)

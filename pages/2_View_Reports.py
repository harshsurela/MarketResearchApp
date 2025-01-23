# pages/2_View_Reports.py

import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add parent directory to path to import from src
file_path = Path(__file__).parent.parent
sys.path.append(str(file_path))

st.set_page_config(
    page_title="View Market Research Reports",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_reports():
    """Load all saved reports from the reports directory"""
    reports = []
    try:
        if os.path.exists("reports"):
            for filename in sorted(os.listdir("reports"), reverse=True):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join("reports", filename), "r", encoding='utf-8') as f:
                            report_data = json.load(f)
                            # Add filename to report data
                            report_data['filename'] = filename
                            reports.append(report_data)
                    except Exception as e:
                        logging.error(f"Error loading report {filename}: {str(e)}")
                        continue
    except Exception as e:
        logging.error(f"Error accessing reports directory: {str(e)}")
        st.error(f"Error loading reports: {str(e)}")
    return reports

def display_references(references):
    """Display references in an organized format"""
    st.header("📚 References")
    for i, ref in enumerate(references, 1):
        with st.expander(f"Reference {i}: {ref['title']}", expanded=False):
            st.write(f"**Source:** {ref['source']}")
            st.markdown(f"**URL:** [{ref['url']}]({ref['url']})")
            st.write(f"**Summary:** {ref['snippet']}")
            if ref.get('published_date'):
                st.write(f"**Published:** {ref['published_date']}")

def format_timestamp_from_filename(filename):
    """Extract and format timestamp from filename"""
    try:
        timestamp_str = filename.split('_')[0]
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Date unknown"

def main():
    st.title("📚 View Market Research Reports")
    st.markdown("""
    Browse and analyze previously generated market research reports.
    Select a report from the list below to view its contents.
    """)

    # Load all reports
    reports = load_reports()

    if not reports:
        st.info("📂 No reports found. Go to the Generate Report page to create your first report!")
        return

    # Sidebar filters
    st.sidebar.header("📊 Report Filters")

    # Search by keyword
    search_term = st.sidebar.text_input("🔍 Search Reports", "").lower()

    # Filter reports based on search term
    if search_term:
        filtered_reports = [
            report for report in reports
            if search_term in report['topic'].lower()
        ]
    else:
        filtered_reports = reports

    # Display number of reports found
    st.sidebar.write(f"Found {len(filtered_reports)} reports")

    # Main content area
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Select a Report")
        # Create selection for reports
        report_options = {
            f"{report['topic']} ({format_timestamp_from_filename(report['filename'])})": report
            for report in filtered_reports
        }

        if report_options:
            selected_report_name = st.radio(
                "Available Reports",
                options=list(report_options.keys()),
                key="report_selector"
            )
            selected_report = report_options[selected_report_name]
        else:
            st.warning("No reports match your search criteria")
            return

    # Display selected report
    with col2:
        if selected_report:
            st.header(f"📄 {selected_report['topic']}")

            # Display metadata
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.caption(f"Generated: {format_timestamp_from_filename(selected_report['filename'])}")
            with col_meta2:
                # Add download button
                st.download_button(
                    label="📥 Download Report",
                    data=json.dumps(selected_report, indent=2),
                    file_name=f"market_research_{selected_report['topic'].replace(' ', '_')}.json",
                    mime="application/json"
                )

            # Display report content
            st.markdown("---")
            st.markdown(selected_report['content'])
            st.markdown("---")

            # Display references
            if 'references' in selected_report:
                display_references(selected_report['references'])

if __name__ == "__main__":
    main()

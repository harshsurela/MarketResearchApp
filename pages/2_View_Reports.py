import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

def load_report(filename: str) -> dict:
    """Load report from JSON file"""
    try:
        with open(os.path.join("reports", filename), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading report: {str(e)}")
        return None

def display_report_content(report_data: dict):
    """Display report content in a structured way"""
    try:
        st.title(report_data['topic'])
        st.write(f"Generated on: {report_data['metadata']['generated_date'][:10]}")

        # Display table of contents
        st.header("Table of Contents")
        for section_name in report_data['content'].keys():
            st.write(f"- {section_name}")

        # Display each section with its charts
        for section_name, content in report_data['content'].items():
            with st.expander(f"📄 {section_name}", expanded=True):
                # Display section content
                st.markdown(content)

                # Display charts if available
                if section_name in report_data.get('charts', {}) and report_data['charts'][section_name]:
                    st.subheader("📊 Charts and Visualizations")
                    for chart_base64 in report_data['charts'][section_name]:
                        if chart_base64:  # Check if chart data exists
                            st.image(chart_base64)

    except Exception as e:
        st.error(f"Error displaying report content: {str(e)}")

def view_reports_page():
    st.title("📚 View Reports")

    # Get list of reports
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        st.warning("No reports found. Generate some reports first!")
        return

    report_files = [f for f in os.listdir(reports_dir) if f.endswith('.json')]

    if not report_files:
        st.warning("No reports found. Generate some reports first!")
        return

    # Create reports dataframe
    report_data = []
    for filename in report_files:
        try:
            report = load_report(filename)
            if report:  # Only add if report loaded successfully
                report_data.append({
                    'Date': datetime.strptime(
                        filename.split('_')[0],
                        '%Y%m%d'
                    ).strftime('%Y-%m-%d'),
                    'Topic': report['topic'],
                    'Filename': filename,
                    'Generated': report['metadata']['generated_date'][:10]
                })
        except Exception as e:
            st.error(f"Error processing report {filename}: {str(e)}")

    if not report_data:
        st.warning("No valid reports found.")
        return

    df = pd.DataFrame(report_data)

    # Filters in sidebar
    st.sidebar.header("🔍 Filter Reports")

    selected_date = st.sidebar.selectbox(
        "Select Date",
        options=['All'] + sorted(df['Date'].unique().tolist())
    )

    selected_topic = st.sidebar.selectbox(
        "Select Topic",
        options=['All'] + sorted(df['Topic'].unique().tolist())
    )

    # Filter dataframe
    filtered_df = df.copy()
    if selected_date != 'All':
        filtered_df = filtered_df[filtered_df['Date'] == selected_date]
    if selected_topic != 'All':
        filtered_df = filtered_df[filtered_df['Topic'] == selected_topic]

    # Display reports
    st.subheader("📑 Available Reports")

    # Create a table of available reports
    st.dataframe(
        filtered_df[['Date', 'Topic', 'Generated']],
        hide_index=True,
        use_container_width=True
    )

    # Display selected report
    selected_report = st.selectbox(
        "Select a report to view:",
        filtered_df['Filename'].tolist(),
        format_func=lambda x: f"{filtered_df[filtered_df['Filename']==x]['Topic'].iloc[0]} ({filtered_df[filtered_df['Filename']==x]['Date'].iloc[0]})"
    )

    if selected_report:
        report = load_report(selected_report)
        if report:
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                pdf_filename = os.path.splitext(selected_report)[0] + '.pdf'
                if os.path.exists(os.path.join(reports_dir, pdf_filename)):
                    with open(os.path.join(reports_dir, pdf_filename), 'rb') as pdf_file:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_file,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )

            with col2:
                with open(os.path.join(reports_dir, selected_report), 'rb') as json_file:
                    st.download_button(
                        label="📥 Download JSON Report",
                        data=json_file,
                        file_name=selected_report,
                        mime="application/json"
                    )

            # Display report content
            st.markdown("---")
            display_report_content(report)

if __name__ == "__main__":
    try:
        st.set_page_config(
            page_title="View Reports - Market Research Generator",
            page_icon="📊",
            layout="wide"
        )
        view_reports_page()
    except Exception as e:
        st.error(f"Application error: {str(e)}")

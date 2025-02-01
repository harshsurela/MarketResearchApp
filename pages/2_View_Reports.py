import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

def load_report(filename: str) -> dict:
    """Load report from JSON file"""
    with open(os.path.join("reports", filename), 'r', encoding='utf-8') as f:
        return json.load(f)

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
            report_data.append({
                'Date': datetime.strptime(
                    filename.split('_')[0],
                    '%Y%m%d'
                ).strftime('%Y-%m-%d'),
                'Topic': report['topic'],
                'Filename': filename
            })
        except Exception as e:
            st.error(f"Error loading report {filename}: {str(e)}")

    df = pd.DataFrame(report_data)

    # Filters
    st.subheader("🔍 Filter Reports")
    col1, col2 = st.columns(2)

    with col1:
        selected_date = st.selectbox(
            "Select Date",
            options=['All'] + sorted(df['Date'].unique().tolist())
        )

    with col2:
        selected_topic = st.selectbox(
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
    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['Topic']} - {row['Date']}", expanded=False):
            try:
                report = load_report(row['Filename'])

                # Display report content
                st.markdown(report['content'])

                # Download buttons
                col1, col2 = st.columns(2)

                with col1:
                    pdf_filename = os.path.splitext(row['Filename'])[0] + '.pdf'
                    if os.path.exists(os.path.join(reports_dir, pdf_filename)):
                        with open(os.path.join(reports_dir, pdf_filename), 'rb') as pdf_file:
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_file,
                                file_name=pdf_filename,
                                mime="application/pdf"
                            )

                with col2:
                    with open(os.path.join(reports_dir, row['Filename']), 'rb') as json_file:
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_file,
                            file_name=row['Filename'],
                            mime="application/json"
                        )

            except Exception as e:
                st.error(f"Error displaying report: {str(e)}")

if __name__ == "__main__":
    view_reports_page()

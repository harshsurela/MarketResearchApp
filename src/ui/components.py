import streamlit as st

class ReportUI:
    @staticmethod
    def render_sidebar():
        with st.sidebar:
            st.header("Report Configuration")
            report_type = st.selectbox(
                "Report Type",
                ["Market Analysis", "Industry Overview", "Technology Assessment"]
            )
            depth_level = st.slider("Report Depth", 1, 5, 3)
            include_sections = st.multiselect(
                "Sections to Include",
                ["Executive Summary", "Market Overview", "Competitive Analysis",
                 "Technical Analysis", "Financial Projections"]
            )
            return report_type, depth_level, include_sections

    @staticmethod
    def render_main_content():
        st.title("Enhanced Market Research Generator")
        topic = st.text_input("Research Topic")
        return topic

import streamlit as st

class ProgressTracker:
    def __init__(self):
        self.progress_bar = None
        self.status_text = None

    def initialize(self):
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()

    def update_progress(self, stage, progress):
        stages = {
            "research": "Conducting Research",
            "analysis": "Analyzing Data",
            "writing": "Writing Report",
            "formatting": "Formatting Content"
        }
        self.status_text.text(f"Stage: {stages.get(stage, stage)}")
        self.progress_bar.progress(progress)

import streamlit as st
from datetime import datetime
import time
from src.thinking_module import BrainStormEngine
from src.retrieval import GoogleRetrieval
from src.llm import GroqLLM


def initialize_session():
    if "active_session" not in st.session_state:
        st.session_state.active_session = False
    if "research_progress" not in st.session_state:
        st.session_state.research_progress = []
    if "toc" not in st.session_state:
        st.session_state.toc = []
    if "llm" not in st.session_state:
        # Initialize GroqLLM with multiple API keys
        api_keys = [
            st.secrets.get(f"GROQ_API_KEY_{i}") for i in range(1, 6)
        ]
        print(api_keys)
        st.session_state.llm = GroqLLM(api_keys=api_keys)
    if "retriever" not in st.session_state:
        st.session_state.retriever = GoogleRetrieval(st.secrets["GOOGLE_API_KEY"], st.secrets["GOOGLE_CSE_ID"])

def sidebar_navigation():
    with st.sidebar:
        st.title("Navigation")

        # New Session Button
        if st.button("+ New Session", use_container_width=True):
            st.session_state.active_session = True
            st.session_state.research_progress = []
            st.rerun()

        # Navigation Links
        st.button("🔍 Discover", use_container_width=True)
        st.button("📚 My Library", use_container_width=True)

        # Table of Contents
        if st.session_state.toc:
            st.markdown("### Table of Contents")
            for item in st.session_state.toc:
                st.markdown(f"- {item}")

def display_thinking_progress():
    print("In display")
    progress = st.progress(0)
    status = st.empty()

    stages = [
        ("Knowledge Curation", "Gathering and organizing information..."),
        ("Outline Generation", "Creating detailed outline..."),
        ("Report Generation", "Generating comprehensive report..."),
        ("Content Polish", "Polishing and refining content...")
    ]

    for i, (stage, message) in enumerate(stages):
        status.write(f"**{stage}:** {message}")
        progress.progress((i + 1) * 25)
        time.sleep(1)

def main():
    st.set_page_config(page_title="Research Brainstorming", layout="wide")
    initialize_session()

    # Sidebar Navigation
    sidebar_navigation()

    # Main Content
    st.title("🧠 Research Brainstorming")

    if not st.session_state.active_session:
        st.info("Click '+ New Session' to start a new research session")
        return

    # Topic Input
    topic = st.text_input("Research Topic", placeholder="Enter your research topic...")

    # Advanced Settings
    with st.expander("Advanced Settings"):
        col1, col2, col3 = st.columns(3)
        with col1:
            max_tokens = st.slider("Max Tokens", 1000, 4096, 2000)
        with col2:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
        with col3:
            research_depth = st.select_slider(
                "Research Depth",
                options=["Basic", "Standard", "Comprehensive"],
                value="Standard"
            )

    if topic and st.button("Start Research"):
        try:
            # Initialize BrainStorm Engine
            engine = BrainStormEngine(
                st.session_state.llm,
                st.session_state.retriever
            )

            # Display thinking progress
            display_thinking_progress()

            # Generate comprehensive report
            report_data = engine.generate_comprehensive_report(
                topic,
                max_tokens=max_tokens,
                temperature=temperature,
                research_depth=research_depth
            )

            # Display results
            st.success("Research completed successfully!")

            # Display outline
            with st.expander("📋 Research Outline", expanded=True):
                st.markdown(report_data["outline"])

            # Display full report
            st.markdown("### 📑 Comprehensive Report")
            st.markdown(report_data["content"])

            # Display references
            with st.expander("📚 References", expanded=False):
                for i, ref in enumerate(report_data["references"], 1):
                    st.markdown(f"{i}. [{ref['title']}]({ref['url']})")

            # Save to session state
            st.session_state.research_progress.append(report_data)

        except Exception as e:
            st.error(f"Error during research: {str(e)}")

if __name__ == "__main__":
    main()

import streamlit as st
from src.config import AppConfig
from src.llm import GroqLLM
from src.retrieval import GoogleRetrieval
from src.generator import ReportGenerator

st.set_page_config(
    page_title="Market Research Generator",
    page_icon="📊",
    layout="wide"
)

def initialize_session_state():
    # Initialize config
    if "config" not in st.session_state:
        st.session_state.config = AppConfig(
            GROQ_API_KEY=st.secrets["GROQ_API_KEY_1"],
            GOOGLE_API_KEY=st.secrets["GOOGLE_API_KEY"],
            GOOGLE_CSE_ID=st.secrets["GOOGLE_CSE_ID"]
        )

    # Initialize generator
    if "generator" not in st.session_state:
        llm = GroqLLM(st.session_state.config.GROQ_API_KEY)
        retriever = GoogleRetrieval(
            st.session_state.config.GOOGLE_API_KEY,
            st.session_state.config.GOOGLE_CSE_ID
        )
        st.session_state.generator = ReportGenerator(llm, retriever)

def main():
    # Always initialize session state first
    initialize_session_state()

    st.title("🎯 Market Research Report Generator")
    st.write("Welcome to the Market Research Report Generator! Use the navigation menu to generate new reports or view existing ones.")

    # Add some example topics
    st.subheader("Popular Research Topics")
    st.write("- Electric Vehicle Market Trends")
    st.write("- Artificial Intelligence in Healthcare")
    st.write("- Renewable Energy Industry Analysis")
    st.write("- Digital Payment Solutions Market")

if __name__ == "__main__":
    main()

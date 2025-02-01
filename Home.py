import streamlit as st
from src.config import AppConfig
from src.llm import GroqLLM
from src.retrieval import GoogleRetrieval
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Market Research Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if "initialized" not in st.session_state:
        try:
            # Load API keys
            groq_api_keys = []
            for i in range(1, 11):
                key = st.secrets.get(f"GROQ_API_KEY_{i}")
                if key and key.strip():
                    groq_api_keys.append(key.strip())

            if not groq_api_keys:
                st.error("No GROQ API keys found in secrets!")
                st.stop()

            # Initialize Config
            st.session_state.config = AppConfig(
                GROQ_API_KEYS=groq_api_keys,
                GOOGLE_API_KEY=st.secrets["GOOGLE_API_KEY"],
                GOOGLE_CSE_ID=st.secrets["GOOGLE_CSE_ID"]
            )

            st.session_state.initialized = True

        except Exception as e:
            st.error(f"Initialization error: {str(e)}")
            st.stop()

async def test_apis_async():
    """Test API connections asynchronously"""
    try:
        # Test GROQ API
        llm = GroqLLM(st.session_state.config.GROQ_API_KEYS)
        st.write("Testing GROQ API connection...")
        st.write(f"Using model: {llm.model}")
        st.write(f"Available models: {llm.supported_models}")

        response = await llm.generate("Test connection", max_retries=1)
        if response:
            st.success("✅ GROQ API connection successful!")
            st.write("Test response:", response[:100] + "...")

        # Test Google API
        retriever = GoogleRetrieval(
            st.session_state.config.GOOGLE_API_KEY,
            st.session_state.config.GOOGLE_CSE_ID
        )
        results = await retriever.search("test query", num_results=1)
        if results:
            st.success("✅ Google API connection successful!")

    except Exception as e:
        st.error(f"API test failed: {str(e)}")
        logging.error(f"API test error details: {str(e)}", exc_info=True)

def test_apis():
    """Wrapper for async API testing"""
    with st.spinner("Testing API connections..."):
        asyncio.run(test_apis_async())

def render_sidebar():
    """Render sidebar content"""
    with st.sidebar:
        st.header("🛠️ Tools")

        if st.button("Test API Connections"):
            test_apis()

        st.markdown("---")

        st.header("📚 Resources")
        st.write("""
        - [Documentation](https://docs.example.com)
        - [API Reference](https://api.example.com)
        - [Support](mailto:support@example.com)
        """)

        st.markdown("---")

        st.header("ℹ️ About")
        st.write("""
        Market Research Generator uses advanced AI to create
        comprehensive market research reports automatically.
        """)

def main():
    initialize_session_state()
    render_sidebar()

    st.title("🎯 Market Research Report Generator")

    st.write("""
    Generate comprehensive market research reports with AI assistance.
    Navigate to the Generate Report page to create a new report.
    """)

    # Main content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Features")
        st.write("""
        - 15-page comprehensive reports
        - Automatic data gathering
        - Professional charts and visualizations
        - Fact-checked content
        - PDF export
        - Source citations
        """)

    with col2:
        st.subheader("🎯 Sample Topics")
        st.write("""
        - Electric Vehicle Market Analysis
        - Renewable Energy Industry
        - AI in Healthcare
        - Digital Payment Solutions
        - Cloud Computing Services
        - IoT Market Trends
        """)

    # Quick start guide
    st.subheader("🚀 Quick Start")
    st.write("""
    1. Navigate to the Generate Report page
    2. Enter your research topic
    3. Click Generate Report
    4. Download the PDF report
    """)

    # Show system status
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")
    st.sidebar.info("✅ System Ready")

if __name__ == "__main__":
    main()

from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import logging
import asyncio
import requests
import streamlit as st
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqLLM:
    def __init__(self, api_keys: List[str], model: str = "mixtral-8x7b-32768"):
        """Initialize the GroqLLM instance with multiple API keys"""
        self.api_keys = [key.strip() for key in api_keys if key.strip()]
        if not self.api_keys:
            raise ValueError("No valid API keys provided")

        self.model = model
        self.api_base = "https://api.groq.com/openai/v1/chat/completions"
        self.current_key_index = 0
        self.last_request_times = {key: datetime.now() for key in self.api_keys}
        self.min_delay_between_requests = 3.0  # Increased to 3 seconds

        logger.info(f"Initialized GroqLLM with {len(self.api_keys)} API keys")
        logger.info(f"Using model: {self.model}")

        # Initialize rate limit tracking
        self.rate_limit_hits = {key: 0 for key in self.api_keys}

    async def generate_section(self, section_name: str, prompt: str,
                             progress_callback: Optional[Callable] = None) -> str:
        """Generate content for a specific section with progress tracking"""
        try:
            if progress_callback:
                progress_callback(f"Starting {section_name}", 0.0)

            logger.info(f"Generating content for section: {section_name}")
            st.write(f"🔄 Generating {section_name}...")

            # Try multiple times with different keys if needed
            max_attempts = len(self.api_keys) * 3  # Allow more attempts
            for attempt in range(max_attempts):
                try:
                    content = await self.generate(prompt)
                    if content and len(content.strip()) > 100:  # Ensure meaningful content
                        if progress_callback:
                            progress_callback(f"Completed {section_name}", 1.0)
                        st.write(f"✅ Completed {section_name}")
                        return content

                    logger.warning(f"Received insufficient content, retrying... (Attempt {attempt + 1})")
                    await asyncio.sleep(3)  # Wait 3 seconds before retry

                except Exception as e:
                    logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                    if "rate limit" in str(e).lower():
                        # st.warning(f"Rate limit hit, waiting 3 seconds before trying next key...")
                        await asyncio.sleep(3)  # Wait 3 seconds on rate limit
                    self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

            raise Exception(f"Failed to generate content for {section_name} after {max_attempts} attempts")

        except Exception as e:
            error_msg = f"Failed to generate {section_name}: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            raise

    async def generate(self, prompt: str) -> str:
        """Generate text using the Groq API with rate limiting and error handling"""
        api_key = self.api_keys[self.current_key_index]

        # Always wait 3 seconds between requests
        await asyncio.sleep(3)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are a professional market research analyst providing detailed and accurate information.
                    Generate comprehensive, well-structured content with specific data points, examples, and insights."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
            "top_p": 0.9
        }

        try:
            logger.info(f"Making API request with key ending in ...{api_key[-4:]}")

            response = requests.post(
                self.api_base,
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                self.last_request_times[api_key] = datetime.now()
                content = response.json()["choices"][0]["message"]["content"]
                logger.info(f"Successfully generated content of length {len(content)}")
                return content

            elif response.status_code == 429:  # Rate limit
                logger.warning(f"Rate limit reached for key ending in ...{api_key[-4:]}")
                # Extract wait time from error message if available
                wait_time = self._extract_wait_time(response.text) or 3
                # st.warning(f"Rate limit reached. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                raise Exception("Rate limit reached")

            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                raise Exception(f"API error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

    def _extract_wait_time(self, error_message: str) -> Optional[float]:
        """Extract wait time from rate limit error message"""
        try:
            match = re.search(r"Please try again in (\d+\.?\d*)s", error_message)
            if match:
                return float(match.group(1))
        except:
            pass
        return None

    async def test_connection(self) -> bool:
        """Test the API connection with all available keys"""
        test_prompt = "Generate a one-sentence test response."

        for i, key in enumerate(self.api_keys):
            try:
                self.current_key_index = i
                response = await self.generate(test_prompt)
                if response:
                    logger.info(f"Successfully tested API key {i+1}")
                    return True
            except Exception as e:
                logger.error(f"Failed to test API key {i+1}: {str(e)}")

        return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration"""
        return {
            "model": self.model,
            "api_keys_count": len(self.api_keys),
            "rate_limit_delay": self.min_delay_between_requests
        }

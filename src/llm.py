# src/llm.py
import requests
from typing import Optional, List
import logging
import time
from datetime import datetime

class GroqLLM:
    def __init__(self, api_keys: List[str], model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the GroqLLM with a list of API keys.

        Args:
            api_keys: List of API keys to rotate through.
            model: The model to use for text generation.
        """
        self.api_keys = api_keys
        self.model = model
        self.api_base = "https://api.groq.com/openai/v1/chat/completions"
        self.current_key_index = 0  # Track the current API key being used
        self.last_request_time = datetime.now()  # Track the last request time
        self.request_delay = 2  # Delay between requests in seconds

    def get_next_api_key(self) -> str:
        """
        Rotate through the list of API keys in a round-robin fashion.
        """
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def generate(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """
        Generate text using the Groq API.

        Args:
            prompt: The input prompt.
            max_retries: Maximum number of retries for failed requests.
            **kwargs: Additional arguments including:
                - max_tokens: Maximum length of generated text.
                - temperature: Temperature for text generation.
                - top_p: Top p sampling parameter.
        """
        headers = {
            "Authorization": f"Bearer {self.get_next_api_key()}",  # Use the next API key
            "Content-Type": "application/json"
        }

        # Format messages according to Groq's chat completion format
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional market research analyst providing detailed and accurate information."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": float(kwargs.get("temperature", 0.7)),
            "max_tokens": int(kwargs.get("max_tokens", 2000)),
            "top_p": float(kwargs.get("top_p", 0.9))
        }

        retry_count = 0
        while retry_count < max_retries:
            try:
                # Ensure we respect the rate limit by delaying requests
                time_since_last_request = (datetime.now() - self.last_request_time).total_seconds()
                if time_since_last_request < self.request_delay:
                    time.sleep(self.request_delay - time_since_last_request)

                # Print debug information before making the request
                logging.debug(f"Making request to: {self.api_base}")
                logging.debug(f"Request headers: {headers}")
                logging.debug(f"Request data: {data}")

                response = requests.post(
                    self.api_base,
                    headers=headers,
                    json=data,
                    timeout=60
                )

                # Print debug information
                logging.debug(f"API Response Status: {response.status_code}")
                logging.debug(f"API Response: {response.text[:500]}...")

                response.raise_for_status()  # Raise exception for bad status codes

                response_json = response.json()
                self.last_request_time = datetime.now()  # Update last request time
                return response_json["choices"][0]["message"]["content"]

            except requests.exceptions.RequestException as e:
                logging.error(f"Request error details: {str(e)}")
                if hasattr(e.response, 'text'):
                    logging.error(f"Error response: {e.response.text}")

                retry_count += 1
                if retry_count < max_retries:
                    logging.info(f"Retrying request ({retry_count}/{max_retries})...")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    raise Exception(f"Error calling Groq API: {str(e)}")
            except Exception as e:
                logging.error(f"General error details: {str(e)}")
                raise Exception(f"Error processing Groq response: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test the connection to the Groq API.
        Returns True if successful, False otherwise.
        """
        try:
            response = self.generate(
                "Hello, this is a test message.",
                max_tokens=10,
                temperature=0.7
            )
            return True
        except Exception as e:
            logging.error(f"Connection test failed: {str(e)}")
            return False

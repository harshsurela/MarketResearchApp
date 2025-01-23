# src/config.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_CSE_ID: str  # Custom Search Engine ID
    DEFAULT_MODEL: str = "llama2-70b-4096"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9

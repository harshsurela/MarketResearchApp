from dataclasses import dataclass
from typing import List

@dataclass
class Persona:
    name: str
    description: str
    expertise: List[str]
    perspective: str

class PersonaGenerator:
    def __init__(self):
        self.default_personas = {
            "market_research": [
                Persona(
                    name="Industry Analyst",
                    description="Expert in market trends and industry analysis",
                    expertise=["Market Analysis", "Industry Trends", "Competitive Intelligence"],
                    perspective="Statistical and analytical approach to market research"
                ),
                Persona(
                    name="Technology Strategist",
                    description="Focuses on technological implications and innovations",
                    expertise=["Technology Trends", "Digital Transformation", "Tech Implementation"],
                    perspective="Technology-driven market analysis"
                ),
                Persona(
                    name="Business Consultant",
                    description="Provides business strategy and operational insights",
                    expertise=["Business Strategy", "Operations", "Process Optimization"],
                    perspective="Business-oriented market analysis"
                ),
                Persona(
                    name="Customer Experience Specialist",
                    description="Focuses on customer needs and behavior",
                    expertise=["User Research", "Customer Behavior", "Market Needs"],
                    perspective="Customer-centric market analysis"
                ),
                Persona(
                    name="Financial Analyst",
                    description="Analyzes market from financial perspective",
                    expertise=["Financial Analysis", "Market Valuation", "Investment Trends"],
                    perspective="Financial market analysis"
                )
            ]
        }

    def get_personas_for_topic(self, topic: str) -> List[Persona]:
        """Generate relevant personas for the given topic"""
        # For now, return default market research personas
        return self.default_personas["market_research"]

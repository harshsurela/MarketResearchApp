from dataclasses import dataclass,field
from typing import List, Dict, Any

REPORT_SECTIONS = {
    "Executive Summary": {
        "length": "1 page",
        "position": 1,
        "include_charts": False,
        "prompt_template": """
            Create a comprehensive executive summary for a market research report on {topic}.

            Requirements:
            1. Length: Approximately 500 words
            2. Must include:
                - Key market insights and findings
                - Critical market statistics and data points
                - Major trends and developments
                - Growth projections
                - Key challenges and opportunities
                - Strategic recommendations
                - Future outlook

            Format:
            - Use professional business language
            - Include specific numbers and percentages
            - Highlight key findings in bullet points
            - Provide actionable insights
            - Focus on quantifiable data

            Make this executive summary compelling and data-driven while maintaining professional tone.
        """
    },
    "Industry Overview": {
        "length": "2 pages",
        "position": 2,
        "include_charts": True,
        "prompt_template": """
            Provide a detailed industry overview for {topic}.

            Required sections:
            1. Industry Definition and Scope
                - Clear definition of the industry
                - Market segmentation
                - Industry boundaries and classifications

            2. Historical Development
                - Industry evolution
                - Key milestones and developments
                - Historical growth patterns

            3. Market Size and Growth
                - Current market size (in USD)
                - Historical growth rates
                - Regional market distribution
                - Market share analysis

            4. Industry Structure
                - Value chain analysis
                - Key stakeholders
                - Distribution channels
                - Industry concentration

            5. Economic Impact
                - Contribution to GDP
                - Employment statistics
                - Economic multiplier effects
                - Trade dynamics

            Format:
            - Length: Approximately 1000 words
            - Include specific data points and statistics
            - Use tables for market size data
            - Include growth rate charts
            - Cite reliable sources
        """
    },
    "Market Analysis": {
        "length": "2 pages",
        "position": 3,
        "include_charts": True,
        "prompt_template": """
            Conduct a comprehensive market analysis for {topic}.

            Required Components:
            1. Market Dynamics
                - Demand drivers
                - Supply factors
                - Pricing trends
                - Market equilibrium analysis

            2. Market Segmentation
                - Customer segments
                - Product segments
                - Geographic segments
                - Market share by segment

            3. Demand Analysis
                - Customer needs and preferences
                - Purchase patterns
                - Demand forecasting
                - Seasonal trends

            4. Supply Analysis
                - Production capacity
                - Supply chain analysis
                - Cost structure
                - Supply constraints

            5. Price Analysis
                - Pricing strategies
                - Price elasticity
                - Price trends
                - Cost-price relationships

            Format:
            - Include market size data
            - Provide growth projections
            - Use charts for trend analysis
            - Include competitive positioning maps
            Length: Approximately 1000 words
        """
    },
    "Competitive Landscape": {
        "length": "2 pages",
        "position": 4,
        "include_charts": True,
        "prompt_template": """
            Analyze the competitive landscape for {topic}.

            Required Sections:
            1. Market Structure
                - Number of competitors
                - Market concentration
                - Entry barriers
                - Industry rivalry

            2. Competitor Analysis
                - Major players profiles
                - Market share analysis
                - Competitive strategies
                - SWOT analysis

            3. Competitive Dynamics
                - Price competition
                - Product differentiation
                - Innovation patterns
                - Market positioning

            4. Strategic Groups
                - Group mapping
                - Strategic positioning
                - Group mobility barriers
                - Performance analysis

            Format:
            - Include competitor comparison tables
            - Provide market share charts
            - Map strategic groups
            - Analyze competitive advantages
            Length: Approximately 1000 words
        """
    },
    "Technology and Innovation": {
        "length": "1 page",
        "position": 5,
        "include_charts": True,
        "prompt_template": """
            Analyze technology trends and innovation in {topic}.

            Cover:
            1. Current Technology Landscape
                - Key technologies
                - Technology adoption rates
                - Innovation trends

            2. Emerging Technologies
                - New developments
                - Potential impacts
                - Adoption timeline

            3. Innovation Analysis
                - R&D trends
                - Patent analysis
                - Innovation leaders

            4. Digital Transformation
                - Digital adoption
                - Technology integration
                - Future outlook

            Format:
            - Include technology roadmaps
            - Patent trend analysis
            - Innovation metrics
            Length: Approximately 500 words
        """
    },
    "Financial Analysis": {
        "length": "1 page",
        "position": 6,
        "include_charts": True,
        "prompt_template": """
            Provide detailed financial analysis for {topic}.

            Include:
            1. Financial Metrics
                - Revenue trends
                - Profitability analysis
                - Cost structure
                - Investment patterns

            2. Market Economics
                - Industry profitability
                - Cost drivers
                - Economic indicators
                - Financial forecasts

            Format:
            - Include financial charts
            - Provide trend analysis
            - Show key metrics
            Length: Approximately 500 words
        """
    },
    "Market Drivers and Trends": {
        "length": "1 page",
        "position": 7,
        "include_charts": True,
        "prompt_template": """
            Analyze key market drivers and trends for {topic}.

            Cover:
            1. Growth Drivers
                - Economic factors
                - Demographic trends
                - Technology impacts
                - Policy influences

            2. Market Trends
                - Consumer trends
                - Industry trends
                - Innovation trends
                - Regulatory trends

            Format:
            - Include trend analysis charts
            - Provide impact assessment
            - Quantify trends where possible
            Length: Approximately 500 words
        """
    },
    "Risk Assessment": {
        "length": "1 page",
        "position": 8,
        "include_charts": True,
        "prompt_template": """
            Conduct a comprehensive risk assessment for {topic}.

            Include:
            1. Risk Categories
                - Market risks
                - Operational risks
                - Financial risks
                - Regulatory risks

            2. Risk Analysis
                - Impact assessment
                - Probability analysis
                - Mitigation strategies
                - Risk monitoring

            Format:
            - Include risk matrices
            - Provide mitigation strategies
            - Risk prioritization
            Length: Approximately 500 words
        """
    },
    "Regulatory Environment": {
        "length": "1 page",
        "position": 9,
        "include_charts": False,
        "prompt_template": """
            Analyze the regulatory environment for {topic}.

            Cover:
            1. Current Regulations
                - Key regulations
                - Compliance requirements
                - Regulatory bodies

            2. Regulatory Trends
                - Upcoming regulations
                - Policy changes
                - Impact analysis

            Format:
            - Include regulatory timeline
            - Compliance requirements
            - Impact assessment
            Length: Approximately 500 words
        """
    },
    "Growth Opportunities": {
        "length": "1 page",
        "position": 10,
        "include_charts": True,
        "prompt_template": """
            Identify and analyze growth opportunities in {topic}.

            Include:
            1. Market Opportunities
                - New segments
                - Geographic expansion
                - Product development

            2. Growth Strategies
                - Market penetration
                - Market development
                - Diversification

            Format:
            - Include opportunity assessment
            - Growth potential analysis
            - Strategic recommendations
            Length: Approximately 500 words
        """
    },
    "Market Forecasts": {
        "length": "1 page",
        "position": 11,
        "include_charts": True,
        "prompt_template": """
            Provide detailed market forecasts for {topic}.

            Include:
            1. Market Projections
                - Size forecasts
                - Growth rates
                - Segment forecasts

            2. Forecast Analysis
                - Key assumptions
                - Scenario analysis
                - Impact factors

            Format:
            - Include forecast charts
            - Scenario analysis
            - Growth projections
            Length: Approximately 500 words
        """
    },
    "Strategic Recommendations": {
        "length": "1 page",
        "position": 12,
        "include_charts": False,
        "prompt_template": """
            Provide strategic recommendations for {topic}.

            Include:
            1. Strategic Options
                - Market strategies
                - Competitive strategies
                - Growth strategies

            2. Implementation
                - Action plans
                - Timeline
                - Resource requirements

            Format:
            - Include prioritized recommendations
            - Implementation roadmap
            - Success metrics
            Length: Approximately 500 words
        """
    },
    "Implementation Roadmap": {
        "length": "1 page",
        "position": 13,
        "include_charts": True,
        "prompt_template": """
            Create a detailed implementation roadmap for {topic}.

            Include:
            1. Implementation Plan
                - Phase breakdown
                - Timeline
                - Resources needed

            2. Success Metrics
                - KPIs
                - Milestones
                - Monitoring plan

            Format:
            - Include timeline charts
            - Resource allocation
            - Success criteria
            Length: Approximately 500 words
        """
    },
    "Success Factors": {
        "length": "0.5 page",
        "position": 14,
        "include_charts": False,
        "prompt_template": """
            Identify critical success factors for {topic}.

            Include:
            1. Key Success Factors
                - Market factors
                - Operational factors
                - Strategic factors

            2. Best Practices
                - Industry benchmarks
                - Success stories
                - Lessons learned

            Format:
            - Include success criteria
            - Best practices
            - Implementation tips
            Length: Approximately 250 words
        """
    },
    "Appendices and References": {
        "length": "0.5 page",
        "position": 15,
        "include_charts": False,
        "prompt_template": """
            Compile appendices and references for {topic}.

            Include:
            1. Data Sources
                - Primary sources
                - Secondary sources
                - Industry reports

            2. Methodology
                - Research approach
                - Data collection
                - Analysis methods

            Format:
            - Include source citations
            - Methodology details
            - Additional data
            Length: Approximately 250 words
        """
    }
}

@dataclass
class ReportConfig:
    target_pages: int = 15
    min_words_per_page: int = 500
    max_words_per_page: int = 600
    include_charts: bool = True
    include_citations: bool = True
    cross_reference_sources: int = 3
    fact_check_confidence: float = 0.8
    sections: Dict = field(default_factory=lambda: REPORT_SECTIONS)

@dataclass
class LLMConfig:
    max_tokens_per_request: int = 1000
    tokens_per_minute: int = 5000
    requests_per_minute: int = 50
    cooldown_time: float = 10.0

@dataclass
class PDFConfig:
    template_path: str = "templates/report_template.html"
    font_family: str = "Arial"
    header_font: str = "Arial Bold"
    normal_font_size: int = 11
    header_font_size: int = 14
    line_spacing: float = 1.5
    margin_top: str = "1in"
    margin_bottom: str = "1in"
    margin_left: str = "1in"
    margin_right: str = "1in"
    include_cover_page: bool = True
    include_toc: bool = True
    include_page_numbers: bool = True
    primary_color: str = "#1a73e8"
    secondary_color: str = "#4285f4"
    text_color: str = "#202124"
    chart_colors: List[str] = field(default_factory=lambda: [
        "#1a73e8", "#4285f4", "#34a853", "#fbbc04", "#ea4335",
        "#185abc", "#5f6368", "#202124", "#9aa0a6", "#80868b"
    ])

@dataclass
class AppConfig:
    GROQ_API_KEYS: List[str]
    GOOGLE_API_KEY: str
    GOOGLE_CSE_ID: str
    MODEL: str = "deepseek-r1-distill-llama-70b	"  # Updated default model
    MAX_TOKENS: int = 32768
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    report_config: ReportConfig = field(default_factory=ReportConfig)
    pdf_config: PDFConfig = field(default_factory=PDFConfig)

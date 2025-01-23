from dataclasses import dataclass
from typing import List, Dict, Any
import logging
import datetime
import streamlit as st


@dataclass
class ThinkingModule:
    """Base class for thinking modules"""
    name: str
    description: str

class KnowledgeCuration(ThinkingModule):
    def __init__(self, llm, retriever):
        super().__init__(
            name="Knowledge Curation",
            description="Curates and organizes knowledge from various sources"
        )
        self.llm = llm
        self.retriever = retriever

    def curate(self, topic: str) -> Dict[str, Any]:
        try:
            # Gather initial information
            search_results = self.retriever.search(topic)

            # Create knowledge curation prompt
            prompt = f"""Research and organize knowledge about {topic}.
            Consider:
            1. Key concepts and definitions
            2. Historical context and development
            3. Current state and applications
            4. Future trends and possibilities
            5. Challenges and limitations

            Based on these sources:
            {self.retriever.format_results_for_prompt(search_results)}
            """
            curated_knowledge = self.llm.generate(prompt)
            return {
                "curated_content": curated_knowledge,
                "sources": search_results
            }
        except Exception as e:
            logging.error(f"Knowledge curation error: {str(e)}")
            raise

class OutlineGeneration(ThinkingModule):
    def __init__(self, llm):
        super().__init__(
            name="Outline Generation",
            description="Generates detailed hierarchical outlines"
        )
        self.llm = llm

    def generate_outline(self, topic: str, curated_knowledge: str) -> str:
        try:
            prompt = f"""Based on the following curated knowledge about {topic},
            create a detailed hierarchical outline with main sections and subsections.

            Curated Knowledge:
            {curated_knowledge}

            Create a comprehensive outline following this structure:
            1. Executive Summary
            2. Introduction and Background
            3. Market Analysis
            4. Technical Analysis
            5. Implementation and Strategy
            6. Future Outlook
            7. Recommendations
            8. Conclusion
            """

            return self.llm.generate(prompt)
        except Exception as e:
            logging.error(f"Outline generation error: {str(e)}")
            raise

class ReportGeneration(ThinkingModule):
    def __init__(self, llm):
        super().__init__(
            name="Report Generation",
            description="Generates detailed reports from outline and knowledge"
        )
        self.llm = llm

    def generate_report(self, topic: str, outline: str, curated_knowledge: str) -> str:
        try:
            prompt = f"""Generate a comprehensive report about {topic} following this outline:

            {outline}

            Using this curated knowledge:
            {curated_knowledge}

            Guidelines:
            - Use formal academic language
            - Include specific examples and case studies
            - Cite sources appropriately
            - Provide data-driven insights
            - Include actionable recommendations
            """

            return self.llm.generate(prompt)
        except Exception as e:
            logging.error(f"Report generation error: {str(e)}")
            raise

class ArticlePolish(ThinkingModule):
    def __init__(self, llm):
        super().__init__(
            name="Article Polish",
            description="Polishes and refines generated content"
        )
        self.llm = llm

    def polish(self, content: str) -> str:
        try:
            prompt = f"""Polish and enhance the following content. Focus on:
            1. Clarity and coherence
            2. Professional tone
            3. Consistent formatting
            4. Proper transitions
            5. Technical accuracy

            Content to polish:
            {content}
            """

            return self.llm.generate(prompt)
        except Exception as e:
            logging.error(f"Article polishing error: {str(e)}")
            raise
import streamlit as st
class BrainStormEngine:
    def __init__(self, llm, retriever):
        self.knowledge_curation = KnowledgeCuration(llm, retriever)
        self.outline_generation = OutlineGeneration(llm)
        self.report_generation = ReportGeneration(llm)
        self.article_polish = ArticlePolish(llm)
        self.llm = llm
        self.retriever = retriever

    def generate_comprehensive_report(self, topic: str, **kwargs) -> Dict[str, Any]:
        try:
            # Step 1: Knowledge Curation
            st.write("📚 Curating knowledge...")
            curated_data = self.knowledge_curation.curate(topic)

            # Step 2: Outline Generation
            st.write("📝 Generating outline...")
            outline = self.outline_generation.generate_outline(
                topic,
                curated_data["curated_content"]
            )

            # Step 3: Report Generation
            st.write("📊 Generating report...")
            report = self.report_generation.generate_report(
                topic,
                outline,
                curated_data["curated_content"]
            )

            # Step 4: Polish Content
            st.write("✨ Polishing content...")
            polished_report = self.article_polish.polish(report)

            return {
                "topic": topic,
                "outline": outline,
                "content": polished_report,
                "references": curated_data["sources"],
                "metadata": {
                    "generated_date": datetime.datetime.now().isoformat(),
                    "generation_params": kwargs
                }
            }
        except Exception as e:
            logging.error(f"Comprehensive report generation error: {str(e)}")
            raise

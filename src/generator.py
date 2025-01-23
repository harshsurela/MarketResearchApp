# src/generator.py
from typing import Dict, List, Any
from datetime import datetime
from .llm import GroqLLM
from .retrieval import GoogleRetrieval
from .persona import Persona, PersonaGenerator

class ReportGenerator:
    def __init__(self, llm: GroqLLM, retriever: GoogleRetrieval):
        self.llm = llm
        self.retriever = retriever
        self.persona_generator = PersonaGenerator()

    def generate_report(self, topic: str, selected_personas=None, **kwargs) -> Dict[str, Any]:
        # Get personas if not provided
        if not selected_personas:
            selected_personas = self.persona_generator.get_personas_for_topic(topic)[:3]

        all_insights = []
        references = []

        # Gather insights from each persona
        for persona in selected_personas:
            # Search for relevant information
            search_results = self.retriever.search(
                f"{topic} {' '.join(persona.expertise)}"
            )
            references.extend(search_results)

            # Generate persona-specific prompt
            prompt = self._generate_persona_prompt(topic, persona, search_results)

            # Generate insights
            insights = self.llm.generate(
                prompt,
                max_tokens=kwargs.get('max_tokens', 2000),
                temperature=kwargs.get('temperature', 0.7)
            )

            all_insights.append({
                "persona": persona.name,
                "insights": insights
            })

        # Compile final report
        final_report = self._compile_report(topic, all_insights, references)

        return {
            "topic": topic,
            "content": final_report,
            "references": references,
            "personas": [p.name for p in selected_personas],
            "generated_date": datetime.now().isoformat()
        }

    def _generate_persona_prompt(self, topic: str, persona: Persona, search_results: List[Dict]) -> str:
        context = self.retriever.format_results_for_prompt(search_results)

        return f"""As {persona.name}, a {persona.description}, analyze {topic} based on the following information:

{context}

Focus on your areas of expertise:
{', '.join(persona.expertise)}

Provide analysis from your perspective: {persona.perspective}

Please structure your analysis with:
1. Key Insights
2. Market Analysis
3. Recommendations
4. Future Outlook

Use formal language and cite sources using [1], [2], etc."""

    def _compile_report(self, topic: str, insights: List[Dict], references: List[Dict]) -> str:
        # Compile insights into a cohesive report
        sections = [
            f"# Market Research Report: {topic}\n\n",
            "## Executive Summary\n\n",
        ]

        for insight in insights:
            sections.append(f"## Analysis from {insight['persona']}\n\n{insight['insights']}\n\n")

        sections.append("## References\n\n")
        for i, ref in enumerate(references, 1):
            sections.append(f"[{i}] [{ref['title']}]({ref['url']})\n")

        return "\n".join(sections)

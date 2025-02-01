import asyncio
import logging
from typing import Dict, List, Any, Callable
from datetime import datetime
import streamlit as st
from .config import REPORT_SECTIONS
from .utils.chart_generator import ChartGenerator
import matplotlib.pyplot as plt
import io
import base64

class ReportGenerator:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.chart_generator = ChartGenerator()
        self.progress_callback = None
        self.sections = list(REPORT_SECTIONS.keys())

    def _convert_figure_to_base64(self, figure: plt.Figure) -> str:
        """Convert matplotlib figure to base64 string"""
        try:
            buf = io.BytesIO()
            figure.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            plt.close(figure)  # Close the figure to free memory
            return f"data:image/png;base64,{image_base64}"
        except Exception as e:
            logging.error(f"Error converting figure to base64: {str(e)}")
            return ""

    async def generate_full_report(self, topic: str, progress_callback: Callable = None) -> Dict[str, Any]:
        """Generate complete market research report"""
        try:
            self.progress_callback = progress_callback
            self._update_progress("Initializing report generation", 0.05)

            # Validate inputs
            if not topic or not topic.strip():
                raise ValueError("Topic cannot be empty")

            # Step 1: Gather research data
            research_data = await self._gather_research_data(topic)
            if not research_data:
                raise ValueError("No research data could be gathered")
            self._update_progress("Research data gathered", 0.15)

            # Step 2: Generate content for all sections
            sections_content = await self._generate_all_sections(topic, research_data)
            self._update_progress("Content generated", 0.50)

            # Step 3: Generate and process charts
            charts_data = {}
            for section_name, content in sections_content.items():
                try:
                    # Generate charts for this section
                    section_figures = await self.chart_generator.generate_charts(
                        topic, section_name, content
                    )

                    # Convert figures to base64 strings
                    if section_figures:
                        charts_data[section_name] = [
                            self._convert_figure_to_base64(fig)
                            for fig in section_figures
                            if fig is not None
                        ]
                        # Clean up any remaining figures
                        for fig in section_figures:
                            plt.close(fig)
                except Exception as e:
                    logging.error(f"Error generating charts for {section_name}: {str(e)}")
                    charts_data[section_name] = []

            self._update_progress("Charts generated", 0.70)

            # Step 4: Compile final report
            final_report = {
                "topic": topic,
                "content": sections_content,
                "charts": charts_data,
                "metadata": {
                    "generated_date": datetime.now().isoformat(),
                    "sections": self.sections,
                }
            }

            self._update_progress("Report compilation complete", 1.0)
            return final_report

        except Exception as e:
            logging.error(f"Error generating report: {str(e)}")
            raise

    async def _gather_research_data(self, topic: str) -> Dict[str, List[Dict]]:
        """Gather research data for all sections"""
        try:
            research_data = {}
            total_sections = len(self.sections)

            for i, section_name in enumerate(self.sections):
                self._update_progress(
                    f"Researching {section_name}",
                    0.15 * (i / total_sections)
                )

                section_data = await self.retriever.search(
                    f"{topic} {section_name}",
                    num_results=5
                )
                research_data[section_name] = section_data

            return research_data

        except Exception as e:
            logging.error(f"Error gathering research data: {str(e)}")
            raise

    async def _generate_all_sections(self, topic: str, research_data: Dict[str, List[Dict]]) -> Dict[str, str]:
        """Generate content for all sections"""
        try:
            tasks = []
            for section_name in self.sections:
                task = self._generate_section_content(
                    topic,
                    section_name,
                    REPORT_SECTIONS[section_name],
                    research_data.get(section_name, [])
                )
                tasks.append(task)

            section_contents = await asyncio.gather(*tasks)
            return dict(zip(self.sections, section_contents))

        except Exception as e:
            logging.error(f"Error generating sections: {str(e)}")
            raise

    async def _generate_section_content(self,
                                      topic: str,
                                      section_name: str,
                                      section_config: Dict,
                                      research_data: List[Dict]) -> str:
        """Generate content for a single section"""
        try:
            # Calculate progress bounds for this section
            section_index = self.sections.index(section_name)
            progress_base = section_index / len(self.sections)
            progress_range = 1 / len(self.sections)

            # Prepare context and prompt
            context = self.retriever.format_results_for_prompt(research_data)
            prompt = section_config["prompt_template"].format(
                topic=topic,
                context=context
            )

            # Generate content
            content = await self.llm.generate_section(
                section_name,
                prompt,
                lambda status, progress: self._update_progress(
                    f"{status}",
                    progress_base + (progress * progress_range)
                )
            )

            return content

        except Exception as e:
            logging.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def _update_progress(self, status: str, progress: float):
        """Update progress callback if available"""
        if self.progress_callback:
            self.progress_callback(status, progress)

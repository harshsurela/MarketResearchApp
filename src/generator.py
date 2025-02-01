import asyncio
import logging
from typing import Dict, List, Any, Callable
from datetime import datetime
import streamlit as st
from .config import REPORT_SECTIONS
from .utils.chart_generator import ChartGenerator
from concurrent.futures import ThreadPoolExecutor

class ReportGenerator:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.chart_generator = ChartGenerator()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.progress_callback = None
        self.sections = list(REPORT_SECTIONS.keys())  # Initialize sections list

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

            # Step 3: Generate charts
            charts = await self._generate_charts(topic, sections_content)
            self._update_progress("Charts generated", 0.70)

            # Step 4: Compile final report
            final_report = self._compile_report(topic, sections_content, charts, research_data)
            self._update_progress("Report compiled", 1.0)

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
        tasks = []
        for section_name in self.sections:
            task = self._generate_section_content(
                topic,
                section_name,
                REPORT_SECTIONS[section_name],
                research_data.get(section_name, [])
            )
            tasks.append(task)

        try:
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
            # Debug information
            st.write(f"Generating content for {section_name}")

            # Prepare context
            context = self.retriever.format_results_for_prompt(research_data)

            # Format prompt
            prompt = section_config["prompt_template"].format(
                topic=topic,
                context=context
            )

            # Calculate progress
            section_index = self.sections.index(section_name)
            progress_base = section_index / len(self.sections)
            progress_range = 1 / len(self.sections)

            # Generate content with retries
            max_retries = 3
            for retry in range(max_retries):
                try:
                    content = await self.llm.generate_section(
                        section_name,
                        prompt,
                        lambda status, progress: self._update_progress(
                            f"{status}",
                            progress_base + (progress * progress_range)
                        )
                    )

                    if content:
                        return content

                except Exception as e:
                    st.error(f"Attempt {retry + 1}/{max_retries} failed: {str(e)}")
                    if retry < max_retries - 1:
                        st.warning(f"Retrying {section_name}...")
                        await asyncio.sleep(2 ** retry)
                    else:
                        raise

            raise Exception(f"Failed to generate content for {section_name} after {max_retries} attempts")

        except Exception as e:
            st.error(f"Error in {section_name}: {str(e)}")
            logging.error(f"Error generating section {section_name}: {str(e)}")
            raise

    async def _generate_charts(self, topic: str, sections_content: Dict[str, str]) -> Dict[str, Any]:
        """Generate charts for the report"""
        charts = {}
        try:
            for section_name, content in sections_content.items():
                if REPORT_SECTIONS[section_name].get("include_charts", False):
                    section_charts = await self.chart_generator.generate_charts(
                        topic, section_name, content
                    )
                    if section_charts:
                        charts[section_name] = section_charts
            return charts
        except Exception as e:
            logging.error(f"Error generating charts: {str(e)}")
            return charts

    def _compile_report(self,
                       topic: str,
                       sections_content: Dict[str, str],
                       charts: Dict[str, Any],
                       research_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Compile final report"""
        try:
            # Create ordered content
            ordered_content = {}
            for section_name in self.sections:
                if section_name in sections_content:
                    ordered_content[section_name] = sections_content[section_name]

            return {
                "topic": topic,
                "content": ordered_content,
                "charts": charts,
                "metadata": {
                    "generated_date": datetime.now().isoformat(),
                    "sections": self.sections,
                    "sources": self._compile_sources(research_data)
                }
            }

        except Exception as e:
            logging.error(f"Error compiling report: {str(e)}")
            raise

    def _compile_sources(self, research_data: Dict[str, List[Dict]]) -> List[Dict]:
        """Compile all sources used in the report"""
        all_sources = {}
        for sources in research_data.values():
            for source in sources:
                if source.get('url'):
                    all_sources[source['url']] = source
        return list(all_sources.values())

    def _update_progress(self, status: str, progress: float):
        """Update progress callback if available"""
        if self.progress_callback:
            self.progress_callback(status, progress)

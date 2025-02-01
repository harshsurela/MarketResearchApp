import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import re
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ChartGenerator:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.setup_style()

    def setup_style(self):
        """Setup matplotlib style"""
        # Use a basic style instead of seaborn
        plt.style.use('bmh')
        # Configure basic plot settings
        plt.rcParams['figure.figsize'] = [10, 6]
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        # Set color palette manually
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    async def generate_charts(self, topic: str, section_name: str,
                            content: str) -> List[plt.Figure]:
        """Generate charts for a section"""
        try:
            # Extract data from content
            data = await self._extract_data(content)
            if not data:
                return []

            # Generate appropriate charts based on section
            charts = await self._generate_section_charts(
                section_name, data, topic
            )

            return charts

        except Exception as e:
            logging.error(f"Chart generation error for {section_name}: {str(e)}")
            return []

class PromptGenerator:
    def generate_detailed_prompt(self, section, topic, depth_level):
        return f"""
        Provide an in-depth analysis for the {section} of {topic}.

        Required depth: {depth_level * 2000} words minimum

        Include:
        1. Detailed analysis with specific examples
        2. Statistical data and trends
        3. Industry-specific insights
        4. Expert opinions and quotes
        5. Future projections
        6. Actionable recommendations

        Format:
        - Use proper headings and subheadings
        - Include bullet points for key insights
        - Add tables for data presentation
        - Cite sources using [Author, Year] format
        """

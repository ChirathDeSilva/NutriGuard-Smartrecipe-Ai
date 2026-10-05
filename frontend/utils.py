"""
FRONTEND UTILITY: HTML Renderer
===============================
Ensures raw HTML rendered via Streamlit is completely stripped of leading
line whitespace and interior blank lines so CommonMark never converts it into
a markdown code block (<pre><code>).
"""

import streamlit as st


def render_html(html_str: str) -> None:
    """
    Safely renders HTML in Streamlit by stripping leading indentation
    and removing blank lines that would otherwise cause Markdown parsers
    to interpret lines as indented code blocks.
    """
    if not html_str:
        return
    clean_lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    st.markdown("\n".join(clean_lines), unsafe_allow_html=True)

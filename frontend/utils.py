"""
FRONTEND UTILITY: HTML Renderer & Asset Helpers
===============================================
Ensures raw HTML rendered via Streamlit is completely stripped of leading
line whitespace and interior blank lines so CommonMark never converts it into
a markdown code block (<pre><code>). Also provides local image encoding.
"""

import base64
from pathlib import Path
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


def get_image_base64(filepath: str) -> str:
    """
    Reads a local image and encodes it into a standard base64 data URL
    for high-speed offline inline rendering without CORS or path issues.
    """
    path = Path(filepath)
    if path.exists():
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        ext = path.suffix.lower().replace(".", "")
        mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
        return f"data:image/{mime};base64,{data}"
    return ""

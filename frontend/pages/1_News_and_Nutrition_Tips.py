"""
FRONTEND SUBPAGE: News and Nutrition Tips
=========================================
Enterprise Light Theme (FlightSense Style).
Curated healthy recipes, nutrition advice, and food safety news.
Zero emojis used.
"""

import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import requests
from frontend.components.cards import render_tip_card
from frontend.utils import render_html

st.set_page_config(
    page_title="NutriGuard — News and Nutrition Insights",
    layout="wide"
)

# Enterprise Light Theme Styling (FlightSense Style)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #f8fafc !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #0f172a !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

/* Enterprise Input Field */
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #0f172a !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}

/* Radio button row */
[data-testid="stRadio"] > div {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
}

hr {
    border-color: #e2e8f0 !important;
    margin: 16px 0 !important;
}
</style>
""", unsafe_allow_html=True)

# Clean Enterprise Header Banner
render_html("""
<div style="
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px 30px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
">
    <div>
        <div style="font-size: 1.6rem; font-weight: 700; color: #0f172a; letter-spacing: -0.02em;">
            Culinary News and Nutrition Insights
        </div>
        <div style="color: #64748b; font-size: 13.5px; margin-top: 4px;">
            Evidence-based dietary science, culinary safety advisories, and macronutrient balance guidelines.
        </div>
    </div>
    <div style="
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        padding: 8px 16px;
        text-align: right;
    ">
        <div style="color: #1d4ed8; font-size: 12px; font-weight: 700; letter-spacing: 0.04em;">NUTRIGUARD EDITORIAL</div>
        <div style="color: #64748b; font-size: 11px;">Verified Research Archive</div>
    </div>
</div>
""")

API_TIPS_URL = "http://127.0.0.1:8000/api/tips"

col_tab, col_search = st.columns([2, 1.5])

with col_tab:
    selected_tab = st.radio(
        "Browse Categories",
        options=["All Articles", "Nutrition Research", "Food Safety News"],
        horizontal=True
    )

with col_search:
    search_query = st.text_input("Filter by keyword or ingredient", placeholder="e.g. turmeric, allergens, protein", value="")

cat_param = None
if selected_tab == "Nutrition Research":
    cat_param = "tip"
elif selected_tab == "Food Safety News":
    cat_param = "news"

params = {}
if cat_param:
    params["category"] = cat_param
if search_query.strip():
    params["tag"] = search_query.strip()

try:
    response = requests.get(API_TIPS_URL, params=params, timeout=5.0)
    if response.status_code == 200:
        tips_list = response.json()
        if not tips_list:
            st.info("No nutrition articles found matching your filter criteria.")
        else:
            st.caption(f"Showing {len(tips_list)} verified scientific article(s)")
            for tip in tips_list:
                render_tip_card(tip)
    else:
        st.error(f"Failed to fetch tips from server (Status {response.status_code})")
except requests.exceptions.ConnectionError:
    st.warning("Backend service is offline. Displaying cached editorial preview.")
    preview_tips = [
        {
            "title": "The Healing Power of Turmeric in Traditional Cuisine",
            "summary": "Why combining turmeric and black pepper maximizes curcumin bioavailability.",
            "content": "Turmeric combined with black pepper (piperine) and healthy lipids increases curcumin absorption by up to 2000 percent, offering systemic anti-inflammatory benefits.",
            "category": "tip",
            "author": "Dr. Anoma Jayasinghe",
            "tags": "turmeric,spices,inflammation"
        },
        {
            "title": "Food Allergen Safety Standards: Managing Hidden Cross-Contact",
            "summary": "Essential guide to identifying hidden allergens in everyday sauces and seasonings.",
            "content": "Always verify ingredient lists for hidden allergens such as fish flakes in sambols, gluten in soy sauces, and tree nuts in spice blends.",
            "category": "news",
            "author": "Food Safety Standards Board",
            "tags": "allergens,food-safety"
        }
    ]
    for p in preview_tips:
        render_tip_card(p)

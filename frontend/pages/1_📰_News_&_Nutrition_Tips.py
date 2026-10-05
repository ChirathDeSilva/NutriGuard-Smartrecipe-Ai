"""
FRONTEND SUBPAGE: News & Recipe Nutrition Tips
==============================================
Luxury Dark-Gold Theme: Curated healthy recipes, nutrition advice,
and food safety news fetched from GET /api/tips.
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
    page_title="NutriGuard — News & Nutrition Insights",
    page_icon="📰",
    layout="wide"
)

# Luxury Dark-Gold Theme Styling
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c14 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e8ecf4 !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0e18 100%) !important;
    border-right: 1px solid rgba(212, 175, 55, 0.15) !important;
}

/* Luxury Input Field */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(212, 175, 55, 0.25) !important;
    border-radius: 10px !important;
    color: #e8ecf4 !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(212, 175, 55, 0.6) !important;
    box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.15) !important;
}

/* Radio button row */
[data-testid="stRadio"] > div {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(212, 175, 55, 0.18) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
}

hr {
    border-color: rgba(212, 175, 55, 0.12) !important;
    margin: 16px 0 !important;
}
</style>
""", unsafe_allow_html=True)

render_html("""
<div style="
    background: linear-gradient(135deg, #0d1117 0%, #111827 50%, #0d1117 100%);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 18px;
    padding: 26px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
">
    <div>
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
            <span style="font-size:28px;">📰</span>
            <span style="
                font-family: 'Playfair Display', serif;
                font-size: 1.8rem; font-weight: 700;
                background: linear-gradient(135deg, #f0d060 0%, #d4af37 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            ">Culinary News & Nutrition Insights</span>
        </div>
        <div style="color:#64748b; font-size:13px;">
            Evidence-based dietary science, culinary safety advisories, and antioxidant research.
        </div>
    </div>
    <div style="
        background: rgba(212,175,55,0.08);
        border: 1px solid rgba(212,175,55,0.25);
        border-radius: 12px;
        padding: 10px 18px;
        text-align: right;
    ">
        <div style="color:#f0d060; font-size:12px; font-weight:600; letter-spacing:0.05em;">NUTRIGUARD EDITORIAL</div>
        <div style="color:#475569; font-size:11px;">Updated 2026 Edition</div>
    </div>
</div>
""")

API_TIPS_URL = "http://127.0.0.1:8000/api/tips"

# Filter controls
col_tab, col_search = st.columns([2, 1.5])

with col_tab:
    selected_tab = st.radio(
        "Browse Articles",
        options=["All", "Nutrition Tips", "Food & Health News"],
        horizontal=True
    )

with col_search:
    search_query = st.text_input("🔍 Search by keyword or ingredient (e.g. turmeric, allergens, sodium)", value="")

# Determine category filter parameter
cat_param = None
if selected_tab == "Nutrition Tips":
    cat_param = "tip"
elif selected_tab == "Food & Health News":
    cat_param = "news"

params = {}
if cat_param:
    params["category"] = cat_param
if search_query.strip():
    params["tag"] = search_query.strip()

# Fetch tips from backend
try:
    response = requests.get(API_TIPS_URL, params=params, timeout=5.0)
    if response.status_code == 200:
        tips_list = response.json()
        if not tips_list:
            st.info("No nutrition articles found matching your filter criteria.")
        else:
            st.caption(f"Curated archive: **{len(tips_list)}** verified scientific article(s)")
            for tip in tips_list:
                render_tip_card(tip)
    else:
        st.error(f"Failed to fetch tips from server (Status {response.status_code})")
except requests.exceptions.ConnectionError:
    st.warning("⚠️ **Backend is offline!** Showing local cached nutrition insights preview.")
    preview_tips = [
        {
            "title": "The Healing Power of Turmeric in Sri Lankan Cuisine",
            "summary": "Why adding turmeric and black pepper together maximizes bioavailability.",
            "content": "Turmeric combined with black pepper (piperine) and coconut fats increases curcumin absorption by up to 2000%.",
            "category": "tip",
            "author": "Dr. Anoma Jayasinghe",
            "tags": "turmeric,spices,inflammation"
        },
        {
            "title": "2026 Food Allergen Safety: Hidden Sources in Everyday Dining",
            "summary": "Essential guide to spotting hidden allergens like fish flakes and gluten cross-contact.",
            "content": "Always verify ingredient lists for hidden allergens such as Maldive fish flakes in sambols and wheat in seasoning blends.",
            "category": "news",
            "author": "Food Safety Standards Board",
            "tags": "allergens,food-safety"
        }
    ]
    for p in preview_tips:
        render_tip_card(p)

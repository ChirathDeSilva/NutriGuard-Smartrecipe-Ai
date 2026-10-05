"""
FRONTEND SUBPAGE: News & Recipe Nutrition Tips
==============================================
Displays curated healthy recipes, nutrition advice, and food safety news
fetched dynamically from the backend REST API (GET /api/tips).
"""

import sys
import os
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import requests
from frontend.components.cards import render_tip_card

st.set_page_config(
    page_title="News & Nutrition Tips - NutriGuard",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Recipe Nutrition Tips & Food Safety News")
st.markdown("Explore science-backed nutrition tips, meal balancing techniques, and food allergen news.")

API_TIPS_URL = "http://127.0.0.1:8000/api/tips"

# Filter controls
col_tab, col_search = st.columns([2, 1.5])

with col_tab:
    selected_tab = st.radio(
        "Filter Category",
        options=["All", "Nutrition Tips", "Food & Health News"],
        horizontal=True
    )

with col_search:
    search_query = st.text_input("🔍 Search by keyword or tag (e.g. turmeric, allergens, sodium)", value="")

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
            st.info("No nutrition tips or news found matching your current filter.")
        else:
            st.caption(f"Showing **{len(tips_list)}** article(s):")
            for tip in tips_list:
                render_tip_card(tip)
    else:
        st.error(f"Failed to fetch tips from server (Status {response.status_code})")
except requests.exceptions.ConnectionError:
    st.warning("⚠️ **Backend is offline!** Showing local cached nutrition tips preview.")
    # Local fallback preview
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

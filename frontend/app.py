"""
STREAMLIT MAIN PAGE: NutriGuard Multi-Turn Chat & SmartRecipe AI
================================================================
Interactive user interface with sidebar dietary and allergen filters,
quick suggestion chips, multi-turn chat stream, and real-time recipe cards with Plotly charts.
"""

import sys
import os
from pathlib import Path

# Ensure root directory is in sys.path so 'frontend.components...' imports work cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import requests

from frontend.components.cards import render_recipe_card

# Page configuration
st.set_page_config(
    page_title="NutriGuard - SmartRecipe AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown(
    """
    <style>
        .hero-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-radius: 14px;
            padding: 24px 28px;
            color: #ffffff;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
            margin-top: 6px;
            margin-bottom: 12px;
        }
        .agent-pill {
            display: inline-block;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #38bdf8;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .quick-chip {
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 13px;
            color: #334155;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .stButton>button {
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Hero Header Banner
st.markdown(
    """
    <div class="hero-banner">
        <h1 class="hero-title">🛡️ NutriGuard AI</h1>
        <div class="hero-subtitle">
            Agentic Culinary Nutrition, 100% Deterministic Allergen Guardrails & Personalized Recipe Intelligence
        </div>
        <div>
            <span class="agent-pill">🧠 1. NLP Query Agent</span>
            <span class="agent-pill">📚 2. BM25 & TheMealDB Retrieval</span>
            <span class="agent-pill">🛡️ 3. Zero-LLM Safety Guardrail</span>
            <span class="agent-pill">⚖️ 4. Multi-Factor Ranking</span>
            <span class="agent-pill">👨‍🍳 5. Grounded Gemini Chef</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# API Endpoint
BACKEND_URL = "http://127.0.0.1:8000/api/chat"

# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Health & Dietary Controls")
    st.caption("Active constraints are strictly enforced by Agent 3 (Safety Guardrail).")

    # Dietary Lifestyle
    diet_choice = st.selectbox(
        "🥗 Dietary Lifestyle",
        options=["None", "vegan", "vegetarian", "keto"],
        index=0,
        help="Deterministic filter will strictly reject prohibited ingredients."
    )

    # Allergies Multi-select
    allergy_options = ["peanuts", "tree nuts", "dairy", "eggs", "gluten", "fish", "shellfish", "soy", "sesame"]
    selected_allergies = st.multiselect(
        "⚠️ Food Allergies (Zero-Tolerance)",
        options=allergy_options,
        default=[],
        help="All recipes matching these allergens or their synonyms will be blocked 100% of the time."
    )

    # Cooking Time Limit
    max_time = st.slider(
        "⏱️ Max Cooking Time (Minutes)",
        min_value=10,
        max_value=90,
        value=45,
        step=5
    )

    # Calorie Ceiling
    apply_calories = st.checkbox("Enforce Calorie Limit", value=False)
    calorie_limit = None
    if apply_calories:
        calorie_limit = st.slider(
            "🔥 Max Calories per Serving (kcal)",
            min_value=150,
            max_value=1000,
            value=500,
            step=50
        )

    # Cuisine preference
    cuisine_pref = st.selectbox(
        "🌍 Cuisine Preference",
        options=["Any", "Sri Lankan", "Indian", "Italian", "Mexican", "Chinese"],
        index=0
    )

    st.divider()

    # Clear chat session
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("💡 **Quick Navigation:** Use the left sidebar to visit the **📰 News & Nutrition Tips** page!")

# ==============================================================================
# CHAT STATE MANAGEMENT
# ==============================================================================
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {
            "role": "assistant",
            "type": "text",
            "content": (
                "👋 **Welcome to NutriGuard AI!** I am your intelligent culinary nutrition assistant.\n\n"
                "Tell me what ingredients you have at home (e.g., *chicken, coconut milk, dhal, shallots*), "
                "ask about any local or international dish, or click a quick prompt below to start!"
            )
        }
    ]

# ==============================================================================
# QUICK SUGGESTION PROMPTS
# ==============================================================================
st.markdown("##### ⚡ Quick Prompt Suggestions:")
chip_col1, chip_col2, chip_col3, chip_col4, chip_col5, chip_col6 = st.columns(6)

clicked_prompt = None
with chip_col1:
    if st.button("🍕 Pizza", use_container_width=True):
        clicked_prompt = "how to make pizza"
with chip_col2:
    if st.button("🍗 Chicken Curry", use_container_width=True):
        clicked_prompt = "how to make chicken curry"
with chip_col3:
    if st.button("🍲 Dhal Curry", use_container_width=True):
        clicked_prompt = "how to make dhal curry"
with chip_col4:
    if st.button("🫓 Pol Roti", use_container_width=True):
        clicked_prompt = "how to make pol roti"
with chip_col5:
    if st.button("🥞 Hoppers", use_container_width=True):
        clicked_prompt = "how to make hoppers"
with chip_col6:
    if st.button("🍣 Sushi", use_container_width=True):
        clicked_prompt = "how to make sushi"

st.divider()

# Render chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("type") == "recipe_card":
            render_recipe_card(msg["content"], card_key=f"hist_{idx}")
        else:
            st.markdown(msg["content"])

# ==============================================================================
# USER INPUT & CHAT DISPATCH
# ==============================================================================
input_box_prompt = st.chat_input("What would you like to cook? (e.g., I have lentils, turmeric, and coconut milk)")

prompt_to_send = clicked_prompt or input_box_prompt

if prompt_to_send:
    # Append and render user message
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt_to_send})
    with st.chat_message("user"):
        st.markdown(prompt_to_send)

    # Prepare API Request Payload
    diet_param = [diet_choice] if diet_choice != "None" else []
    cuisine_param = cuisine_pref if cuisine_pref != "Any" else None

    # Prepare previous message history for context resolution (exclude current prompt)
    history_payload = []
    for m in st.session_state.messages[:-1][-6:]:
        c_text = m.get("content")
        if isinstance(c_text, dict):
            c_text = f"Recommended Recipe: {c_text.get('recipe_title', '')}"
        history_payload.append({"role": m.get("role", "user"), "content": str(c_text)})

    payload = {
        "user_id": 1,
        "prompt": prompt_to_send,
        "conversation_history": history_payload,
        "dietary_preferences": diet_param,
        "allergies": selected_allergies,
        "max_cooking_time": max_time,
        "calorie_limit": calorie_limit,
        "cuisine_preference": cuisine_param
    }

    # Call FastAPI Orchestrator
    with st.chat_message("assistant"):
        with st.spinner("🤖 NutriGuard Multi-Agent Pipeline verifying food safety & ranking best recipes..."):
            try:
                response = requests.post(BACKEND_URL, json=payload, timeout=45.0)

                if response.status_code == 200:
                    api_data = response.json()
                    response_type = api_data.get("response_type", "recipe_recommendation")

                    if response_type == "conversational":
                        msg_text = api_data.get("message", "Hello! How can I help you?")
                        st.markdown(msg_text)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "type": "text",
                            "content": msg_text
                        })
                    else:
                        card_id = f"card_{len(st.session_state.messages)}"
                        render_recipe_card(api_data, card_key=card_id)

                        # Store in chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "type": "recipe_card",
                            "content": api_data
                        })

                elif response.status_code == 400:
                    err = response.json().get("detail", {})
                    if isinstance(err, dict):
                        st.error(f"🛑 **Food Safety Warning:** {err.get('message', 'Blocked')}")
                        st.markdown(f"**Reason:** {err.get('reason', '')}")
                        violations = err.get("violations", [])
                        if violations:
                            st.markdown("**Specific Violations:**")
                            for v in violations:
                                st.markdown(f"- ⚠️ {v}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "type": "text",
                            "content": f"🛑 **Blocked by Food Safety Guardrail:** {err.get('reason', '')} (Violations: {', '.join(violations)})"
                        })
                    else:
                        st.error(f"Error: {err}")
                        st.session_state.messages.append({"role": "assistant", "type": "text", "content": str(err)})

                elif response.status_code == 404:
                    msg = "🔍 No matching recipes could be found for your requested ingredients."
                    st.warning(msg)
                    st.session_state.messages.append({"role": "assistant", "type": "text", "content": msg})

                else:
                    st.error(f"Server error: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("🚨 **Cannot connect to FastAPI Backend!** Please make sure the backend is running at `http://127.0.0.1:8000`.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

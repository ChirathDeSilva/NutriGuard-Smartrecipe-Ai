"""
STREAMLIT MAIN PAGE: NutriGuard Multi-Turn Chat & SmartRecipe AI
================================================================
Interactive user interface with sidebar dietary and allergen filters,
multi-turn chat stream, and real-time recipe cards with Plotly charts.
"""

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
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #64748b;
            margin-bottom: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-header">🛡️ NutriGuard - SmartRecipe AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Agentic Multi-Agent Recipe Recommendation & 100% Deterministic Food Safety Guardrail</div>',
    unsafe_allow_html=True
)

# API Endpoint
BACKEND_URL = "http://127.0.0.1:8000/api/chat"

# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Dietary & Health Filters")
    st.caption("These filters are strictly enforced by Agent 3 (Safety Guardrail).")

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
        "⚠️ Food Allergies (Zero Tolerance)",
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
        index=1
    )

    st.divider()
    st.caption("💡 **Quick Navigation:** Use the left sidebar to visit the **📰 News & Nutrition Tips** page!")

# ==============================================================================
# CHAT STATE MANAGEMENT
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "type": "text",
            "content": (
                "👋 Hello! I am **NutriGuard AI**. Tell me what ingredients you have at home "
                "(e.g., *chicken, coconut milk, dhal, shallots*) or what kind of meal you are craving. "
                "I will verify all food allergens and compute the best recipe for you!"
            )
        }
    ]

# Render chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("type") == "recipe_card":
            render_recipe_card(msg["content"], card_key=f"hist_{idx}")
        else:
            st.markdown(msg["content"])

# ==============================================================================
# USER INPUT INTERACTION
# ==============================================================================
user_prompt = st.chat_input("What would you like to cook? (e.g., I have lentils, turmeric, and coconut milk)")

if user_prompt:
    # Append and render user message
    st.session_state.messages.append({"role": "user", "type": "text", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Prepare API Request Payload
    diet_param = [diet_choice] if diet_choice != "None" else []
    cuisine_param = cuisine_pref if cuisine_pref != "Any" else None

    payload = {
        "user_id": 1,
        "prompt": user_prompt,
        "dietary_preferences": diet_param,
        "allergies": selected_allergies,
        "max_cooking_time": max_time,
        "calorie_limit": calorie_limit,
        "cuisine_preference": cuisine_param
    }

    # Call FastAPI Orchestrator
    with st.chat_message("assistant"):
        with st.spinner("🤖 NutriGuard Multi-Agent Pipeline processing... (Query -> Retrieval -> Safety -> Ranking -> Response)"):
            try:
                response = requests.post(BACKEND_URL, json=payload, timeout=20.0)

                if response.status_code == 200:
                    recipe_data = response.json()
                    card_id = f"card_{len(st.session_state.messages)}"
                    render_recipe_card(recipe_data, card_key=card_id)

                    # Store in chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "recipe_card",
                        "content": recipe_data
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

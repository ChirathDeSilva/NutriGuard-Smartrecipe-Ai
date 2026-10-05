"""
STREAMLIT MAIN PAGE: NutriGuard Multi-Turn Chat & SmartRecipe AI
================================================================
Premium Luxury UI — Dark Glassmorphism, Gold Accents, Modern Typography
"""

import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import requests

from frontend.components.cards import render_recipe_card
from frontend.utils import render_html

st.set_page_config(
    page_title="NutriGuard AI — SmartRecipe",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LUXURY CSS — Dark Gold Premium Theme
# ============================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">

<style>
/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c14 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e8ecf4 !important;
}

/* ── Hide Streamlit Branding ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar Luxury ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0e18 100%) !important;
    border-right: 1px solid rgba(212, 175, 55, 0.15) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stCheckbox label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* ── Gold Accent on Select/Slider ── */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(212, 175, 55, 0.06) !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 8px !important;
    color: #e8ecf4 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
    border-color: rgba(212, 175, 55, 0.5) !important;
    box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.12) !important;
}
[data-baseweb="slider"] div[role="slider"] {
    background: #d4af37 !important;
    border: 2px solid #f0d060 !important;
}

/* ── Chat Input Bar ── */
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(212, 175, 55, 0.25) !important;
    border-radius: 12px !important;
    color: #e8ecf4 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(212, 175, 55, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.08) !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #d4af37 0%, #b8932a 100%) !important;
    border-radius: 10px !important;
    color: #000 !important;
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(10px) !important;
}

/* ── Metric Cards ── */
[data-testid="metric-container"] {
    background: rgba(212, 175, 55, 0.06) !important;
    border: 1px solid rgba(212, 175, 55, 0.18) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}
[data-testid="metric-container"] label {
    color: #94a3b8 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f0d060 !important;
    font-weight: 700 !important;
    font-size: 18px !important;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(212, 175, 55, 0.14) !important;
    color: #f0d060 !important;
    font-weight: 600 !important;
}

/* ── Info / Warning / Success Boxes ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 3px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: rgba(212, 175, 55, 0.1) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 10px !important;
    color: #f0d060 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: rgba(212, 175, 55, 0.2) !important;
    border-color: rgba(212, 175, 55, 0.55) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(212, 175, 55, 0.15) !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(212, 175, 55, 0.12) !important;
    margin: 12px 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: rgba(212,175,55,0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(212,175,55,0.5); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO HEADER
# ============================================================
render_html("""
<div style="
    background: linear-gradient(135deg, #0d1117 0%, #111827 50%, #0d1117 100%);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 20px;
    padding: 32px 36px 28px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
">
    <div style="position: absolute; top: -60px; left: -60px; width: 200px; height: 200px; background: radial-gradient(circle, rgba(212,175,55,0.12) 0%, transparent 70%); pointer-events: none;"></div>
    <div style="position: absolute; bottom: -60px; right: -60px; width: 200px; height: 200px; background: radial-gradient(circle, rgba(56,189,248,0.07) 0%, transparent 70%); pointer-events: none;"></div>
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
        <div style="background: linear-gradient(135deg, #d4af37, #b8932a); border-radius: 14px; width: 52px; height: 52px; display: flex; align-items: center; justify-content: center; font-size: 26px; box-shadow: 0 4px 20px rgba(212,175,55,0.35); flex-shrink:0;">🛡️</div>
        <div>
            <div style="font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #f0d060 0%, #d4af37 50%, #b8932a 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;">NutriGuard AI</div>
            <div style="color:#64748b; font-size:13px; font-weight:400; letter-spacing:0.04em; margin-top:3px;">
                Precision Culinary Intelligence · Allergen-Safe · Real-Time Recipe AI
            </div>
        </div>
    </div>
    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:16px;">
        <span style="background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.25);color:#d4af37;padding:5px 13px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;">🧠 NLP QUERY AGENT</span>
        <span style="background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.2);color:#38bdf8;padding:5px 13px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;">📚 BM25 + THEMEALDB</span>
        <span style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:#f87171;padding:5px 13px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;">🛡️ ZERO-LLM SAFETY</span>
        <span style="background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.2);color:#c084fc;padding:5px 13px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;">⚖️ MULTI-FACTOR RANK</span>
        <span style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#4ade80;padding:5px 13px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;">👨‍🍳 GEMINI CHEF</span>
    </div>
</div>
""")

BACKEND_URL = "http://127.0.0.1:8000/api/chat"

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    render_html("""
    <div style="
        background: linear-gradient(135deg, rgba(212,175,55,0.1) 0%, rgba(212,175,55,0.04) 100%);
        border: 1px solid rgba(212,175,55,0.18);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 20px;
    ">
        <div style="font-family:'Playfair Display',serif; font-size:15px; font-weight:600; color:#f0d060; margin-bottom:4px;">⚙️ Dietary Controls</div>
        <div style="font-size:11px; color:#475569; line-height:1.5;">All constraints enforced by the <strong style='color:#64748b;'>Zero-LLM Safety Guardrail</strong> — 100% deterministic.</div>
    </div>
    """)

    diet_choice = st.selectbox(
        "🥗 Dietary Lifestyle",
        options=["None", "vegan", "vegetarian", "keto"],
        index=0,
    )

    allergy_options = ["peanuts", "tree nuts", "dairy", "eggs", "gluten", "fish", "shellfish", "soy", "sesame"]
    selected_allergies = st.multiselect(
        "⚠️ Food Allergies (Zero-Tolerance)",
        options=allergy_options,
        default=[],
    )

    max_time = st.slider("⏱️ Max Cooking Time (min)", 10, 90, 45, 5)

    apply_calories = st.checkbox("🔥 Enforce Calorie Limit", value=False)
    calorie_limit = None
    if apply_calories:
        calorie_limit = st.slider("Max Calories (kcal)", 150, 1000, 500, 50)

    cuisine_pref = st.selectbox(
        "🌍 Cuisine Preference",
        options=["Any", "Sri Lankan", "Indian", "Italian", "Mexican", "Chinese"],
        index=0
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    render_html("""
    <div style="margin-top:16px; padding:12px; background:rgba(255,255,255,0.03); border-radius:10px; border:1px solid rgba(255,255,255,0.06);">
        <div style="font-size:11px; color:#475569; line-height:1.6;">
            📰 Visit <strong style='color:#64748b;'>News & Tips</strong> page from left sidebar for nutrition insights.
        </div>
    </div>
    """)

# ============================================================
# CHAT STATE
# ============================================================
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {
            "role": "assistant",
            "type": "text",
            "content": (
                "✨ **Welcome to NutriGuard AI** — your precision culinary intelligence assistant.\n\n"
                "Tell me what ingredients you have at home (e.g., *chicken, coconut milk, lentils, shallots*), "
                "or ask for any local or international recipe. I'll search our database, verify all allergens, "
                "and deliver the perfect dish for you.\n\n"
                "*Click a quick prompt below or type your query to get started!*"
            )
        }
    ]

# ============================================================
# QUICK PROMPT CHIPS
# ============================================================
render_html("""
<div style="margin-bottom:12px;">
    <span style="font-size:11px; font-weight:600; color:#475569; text-transform:uppercase; letter-spacing:0.08em;">⚡ Quick Prompts</span>
</div>
""")

chips = [
    ("🍕", "Pizza", "how to make pizza"),
    ("🍗", "Chicken Curry", "how to make chicken curry"),
    ("🍲", "Dhal Curry", "how to make dhal curry"),
    ("🫓", "Pol Roti", "how to make pol roti"),
    ("🥞", "Hoppers", "how to make hoppers"),
    ("🦞", "Prawn Curry", "how to make prawn curry"),
    ("🍣", "Sushi", "how to make sushi"),
    ("🧆", "Parippu Vada", "how to make parippu vada"),
]

clicked_prompt = None
cols = st.columns(len(chips))
for i, (icon, label, query) in enumerate(chips):
    with cols[i]:
        if st.button(f"{icon} {label}", use_container_width=True, key=f"chip_{i}"):
            clicked_prompt = query

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
st.divider()

# ============================================================
# RENDER CHAT HISTORY
# ============================================================
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("type") == "recipe_card":
            render_recipe_card(msg["content"], card_key=f"hist_{idx}")
        else:
            st.markdown(msg["content"])

# ============================================================
# USER INPUT
# ============================================================
input_box_prompt = st.chat_input("Ask for a recipe, ingredients you have, or any dish... (e.g. 'I have lentils, coconut milk and garlic')")
prompt_to_send = clicked_prompt or input_box_prompt

if prompt_to_send:
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt_to_send})
    with st.chat_message("user"):
        st.markdown(prompt_to_send)

    diet_param = [diet_choice] if diet_choice != "None" else []
    cuisine_param = cuisine_pref if cuisine_pref != "Any" else None

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

    with st.chat_message("assistant"):
        with st.spinner("🤖 NutriGuard pipeline: querying · safety-checking · ranking..."):
            try:
                response = requests.post(BACKEND_URL, json=payload, timeout=45.0)

                if response.status_code == 200:
                    api_data = response.json()
                    response_type = api_data.get("response_type", "recipe_recommendation")

                    if response_type == "conversational":
                        msg_text = api_data.get("message", "Hello! How can I help you?")
                        st.markdown(msg_text)
                        st.session_state.messages.append({"role": "assistant", "type": "text", "content": msg_text})
                    else:
                        card_id = f"card_{len(st.session_state.messages)}"
                        render_recipe_card(api_data, card_key=card_id)
                        st.session_state.messages.append({"role": "assistant", "type": "recipe_card", "content": api_data})

                elif response.status_code == 400:
                    err = response.json().get("detail", {})
                    if isinstance(err, dict):
                        st.error(f"🛑 **Food Safety Warning:** {err.get('message', 'Blocked')}")
                        st.markdown(f"**Reason:** {err.get('reason', '')}")
                        violations = err.get("violations", [])
                        if violations:
                            st.markdown("**Violations detected:**")
                            for v in violations:
                                st.markdown(f"- ⚠️ {v}")
                        st.session_state.messages.append({"role": "assistant", "type": "text", "content": f"🛑 Safety block: {err.get('reason', '')} — Violations: {', '.join(violations)}"})
                    else:
                        st.error(str(err))

                elif response.status_code == 404:
                    msg = "🔍 No matching recipes found for your query. Try different ingredients or a broader request!"
                    st.warning(msg)
                    st.session_state.messages.append({"role": "assistant", "type": "text", "content": msg})

                else:
                    st.error(f"Server error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("🚨 **Backend offline.** Start it with: `uvicorn backend.app.main:app --port 8000 --reload`")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

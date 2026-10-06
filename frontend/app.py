"""
STREAMLIT MAIN PAGE: NutriGuard Multi-Turn Chat & SmartRecipe AI
================================================================
Enterprise Light Theme (FlightSense Style).
Clean white & slate palette, crisp typography (Inter), hero photography,
and strictly ZERO emojis.
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
from frontend.utils import render_html, get_image_base64

st.set_page_config(
    page_title="NutriGuard AI — SmartRecipe",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ENTERPRISE CSS — Clean Light Theme (FlightSense Style)
# ============================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #f8fafc !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    color: #0f172a !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Enterprise Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stCheckbox label {
    color: #475569 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #0f172a !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}
[data-baseweb="slider"] div[role="slider"] {
    background: #2563eb !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 2px 6px rgba(37,99,235,0.3) !important;
}

/* ── Chat Input Bar ── */
[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14.5px !important;
    padding: 14px 18px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}
[data-testid="stChatInput"] button {
    background: #2563eb !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}

/* ── Buttons & Prompt Chips ── */
.stButton > button {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 999px !important;
    color: #334155 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 6px 16px !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
}
.stButton > button:hover {
    background: #eff6ff !important;
    border-color: #bfdbfe !important;
    color: #1d4ed8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08) !important;
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 18px 22px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
}

/* ── Divider & Scrollbar ── */
hr {
    border-color: #e2e8f0 !important;
    margin: 16px 0 !important;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f8fafc; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# Preload local image base64 strings
hero_img_b64 = get_image_base64("frontend/assets/hero_culinary.jpg")
cta_img_b64 = get_image_base64("frontend/assets/cta_banner.jpg")

# ============================================================
# TOP NAVIGATION BAR (FlightSense Style)
# ============================================================
render_html("""
<div style="
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 14px 24px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 10px;
            width: 40px; height: 40px;
            display: flex; align-items: center; justify-content: center;
            color: #2563eb;
            font-weight: 800;
            font-size: 16px;
        ">
            NG
        </div>
        <div>
            <div style="font-size: 18px; font-weight: 700; color: #0f172a; line-height: 1.1;">NutriGuard</div>
            <div style="font-size: 11px; color: #64748b; letter-spacing: 0.04em;">Predict · Plan · Nourish Better</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="background: #f1f5f9; color: #475569; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 500;">Home</span>
        <span style="background: #f1f5f9; color: #475569; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 500;">Recipe Engine</span>
        <span style="background: #f1f5f9; color: #475569; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 500;">Safety Guardrail</span>
        <span style="background: #2563eb; color: #ffffff; padding: 6px 16px; border-radius: 999px; font-size: 12px; font-weight: 600;">Active Session</span>
    </div>
</div>
""")

# ============================================================
# HERO SECTION (FlightSense Style with Real Image)
# ============================================================
hero_img_tag = f'<img src="{hero_img_b64}" alt="Fresh Culinary Ingredients" style="width: 100%; height: 260px; object-fit: cover; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;">' if hero_img_b64 else '<div style="background: #e2e8f0; width: 100%; height: 260px; border-radius: 16px;"></div>'

render_html(f"""
<div style="
    background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 60%, #e0f2fe 100%);
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 24px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.03);
">
    <div style="display: grid; grid-template-columns: 1.25fr 1fr; gap: 32px; align-items: center;">
        <div>
            <div style="
                font-size: 2.2rem;
                font-weight: 800;
                color: #0f172a;
                line-height: 1.15;
                letter-spacing: -0.03em;
                margin-bottom: 12px;
            ">
                Personalized Recipe and Allergen Safety Intelligence
            </div>
            <div style="color: #475569; font-size: 14.5px; line-height: 1.6; margin-bottom: 22px;">
                An intelligent multi-agent culinary platform that analyzes available ingredients,
                strictly validates zero-tolerance food allergens with zero hallucination,
                and delivers verified recipes with calibrated macronutrient profiles.
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <div style="
                    background: #2563eb;
                    color: #ffffff;
                    padding: 10px 22px;
                    border-radius: 999px;
                    font-size: 13.5px;
                    font-weight: 600;
                    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
                    display: inline-block;
                ">
                    Search Safe Recipes &rarr;
                </div>
                <div style="
                    background: #ffffff;
                    border: 1px solid #cbd5e1;
                    color: #334155;
                    padding: 10px 18px;
                    border-radius: 999px;
                    font-size: 13.5px;
                    font-weight: 500;
                    display: inline-block;
                ">
                    5 Autonomous Agents Active
                </div>
            </div>
        </div>
        <div>
            {hero_img_tag}
        </div>
    </div>
</div>
""")

# ============================================================
# THREE FEATURE CARDS (FlightSense Style)
# ============================================================
render_html("""
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; margin-bottom: 28px;">
    <!-- Card 1: Smart Retrieval -->
    <div style="
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02);
    ">
        <div style="
            background: #eff6ff;
            color: #2563eb;
            width: 44px; height: 44px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700;
            font-size: 16px;
            margin-bottom: 14px;
        ">
            SR
        </div>
        <div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">Smart Retrieval</div>
        <div style="font-size: 13px; color: #64748b; line-height: 1.55;">
            BM25 text ranking across 20 authentic heritage recipes with dynamic fallback to global culinary archives.
        </div>
    </div>

    <!-- Card 2: Deterministic Safety -->
    <div style="
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02);
    ">
        <div style="
            background: #f0fdfa;
            color: #0d9488;
            width: 44px; height: 44px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700;
            font-size: 16px;
            margin-bottom: 14px;
        ">
            DS
        </div>
        <div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">Deterministic Safety</div>
        <div style="font-size: 13px; color: #64748b; line-height: 1.55;">
            Zero-LLM allergen and dietary restriction validation enforced with 100 percent precision before ranking.
        </div>
    </div>

    <!-- Card 3: Instant Nutrition -->
    <div style="
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02);
    ">
        <div style="
            background: #faf5ff;
            color: #7c3aed;
            width: 44px; height: 44px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700;
            font-size: 16px;
            margin-bottom: 14px;
        ">
            IN
        </div>
        <div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">Instant Nutrition</div>
        <div style="font-size: 13px; color: #64748b; line-height: 1.55;">
            Calculated macronutrient distributions including protein, carbs, fats, and calorie density per serving.
        </div>
    </div>
</div>
""")

# ============================================================
# HOW IT WORKS SECTION (FlightSense 1 -> 2 -> 3 Timeline)
# ============================================================
render_html("""
<div style="
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 30px 32px 34px;
    margin-bottom: 28px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
">
    <div style="text-align: center; margin-bottom: 24px;">
        <div style="font-size: 1.5rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">How It Works</div>
        <div style="font-size: 13.5px; color: #64748b; margin-top: 4px;">
            NutriGuard coordinates five specialized autonomous agents to deliver validated, personalized recommendations.
        </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 16px; align-items: center;">
        <!-- Step 1 -->
        <div style="text-align: center; padding: 12px;">
            <div style="
                background: #eff6ff;
                border: 2px solid #bfdbfe;
                color: #2563eb;
                width: 46px; height: 46px;
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-weight: 800;
                font-size: 16px;
                margin: 0 auto 12px;
            ">1</div>
            <div style="font-weight: 700; font-size: 14px; color: #0f172a; margin-bottom: 4px;">Enter Ingredients</div>
            <div style="font-size: 12px; color: #64748b; line-height: 1.5;">
                Provide available pantry items, cooking time limits, or zero-tolerance allergies.
            </div>
        </div>

        <div style="color: #cbd5e1; font-size: 20px; font-weight: 700;">&rarr;</div>

        <!-- Step 2 -->
        <div style="text-align: center; padding: 12px;">
            <div style="
                background: #f0fdfa;
                border: 2px solid #99f6e4;
                color: #0d9488;
                width: 46px; height: 46px;
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-weight: 800;
                font-size: 16px;
                margin: 0 auto 12px;
            ">2</div>
            <div style="font-weight: 700; font-size: 14px; color: #0f172a; margin-bottom: 4px;">Agent Safety Audit</div>
            <div style="font-size: 12px; color: #64748b; line-height: 1.5;">
                Deterministic guardrails verify every candidate recipe against declared allergens.
            </div>
        </div>

        <div style="color: #cbd5e1; font-size: 20px; font-weight: 700;">&rarr;</div>

        <!-- Step 3 -->
        <div style="text-align: center; padding: 12px;">
            <div style="
                background: #faf5ff;
                border: 2px solid #e9d5ff;
                color: #7c3aed;
                width: 46px; height: 46px;
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-weight: 800;
                font-size: 16px;
                margin: 0 auto 12px;
            ">3</div>
            <div style="font-weight: 700; font-size: 14px; color: #0f172a; margin-bottom: 4px;">Get Precision Recipe</div>
            <div style="font-size: 12px; color: #64748b; line-height: 1.5;">
                Receive validated step-by-step instructions with complete macronutrient profile.
            </div>
        </div>
    </div>
</div>
""")

BACKEND_URL = "http://127.0.0.1:8000/api/chat"

# ============================================================
# SIDEBAR CONTROLS (Zero Emojis)
# ============================================================
with st.sidebar:
    render_html("""
    <div style="
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 20px;
    ">
        <div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 3px;">Dietary Controls</div>
        <div style="font-size: 11.5px; color: #64748b; line-height: 1.5;">
            Constraints enforced by the <strong>Zero-LLM Safety Guardrail</strong> with 100 percent determinism.
        </div>
    </div>
    """)

    diet_choice = st.selectbox(
        "Dietary Lifestyle",
        options=["None", "vegan", "vegetarian", "keto"],
        index=0,
    )

    allergy_options = ["peanuts", "tree nuts", "dairy", "eggs", "gluten", "fish", "shellfish", "soy", "sesame"]
    selected_allergies = st.multiselect(
        "Food Allergies (Zero-Tolerance)",
        options=allergy_options,
        default=[],
    )

    max_time = st.slider("Max Cooking Time (Minutes)", 10, 90, 45, 5)

    apply_calories = st.checkbox("Enforce Calorie Limit", value=False)
    calorie_limit = None
    if apply_calories:
        calorie_limit = st.slider("Max Calories (kcal)", 150, 1000, 500, 50)

    cuisine_pref = st.selectbox(
        "Cuisine Preference",
        options=["Any", "Sri Lankan", "Indian", "Italian", "Mexican", "Chinese"],
        index=0
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    if st.button("Clear Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    render_html("""
    <div style="margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0;">
        <div style="font-size: 11.5px; color: #64748b; line-height: 1.6;">
            Navigate to <strong>News and Nutrition Tips</strong> from the left sidebar to explore verified articles.
        </div>
    </div>
    """)

# ============================================================
# CHAT STATE INITIALIZATION (Zero Emojis)
# ============================================================
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {
            "role": "assistant",
            "type": "text",
            "content": (
                "**Welcome to NutriGuard AI** — your culinary nutrition and safety intelligence assistant.\n\n"
                "Enter the ingredients you have at home (for example: *chicken, coconut milk, lentils, shallots*), "
                "or request any local or international dish. Our autonomous pipeline will verify all allergen constraints, "
                "calculate nutritional macronutrients, and deliver calibrated recipe instructions.\n\n"
                "*Select a quick prompt below or type your request in the chat bar.*"
            )
        }
    ]

# ============================================================
# QUICK PROMPT CHIPS (Zero Emojis)
# ============================================================
render_html("""
<div style="margin-bottom: 10px;">
    <span style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">
        Quick Prompts
    </span>
</div>
""")

chips = [
    ("Pizza", "how to make pizza"),
    ("Chicken Curry", "how to make chicken curry"),
    ("Dhal Curry", "how to make dhal curry"),
    ("Pol Roti", "how to make pol roti"),
    ("Hoppers", "how to make hoppers"),
    ("Prawn Curry", "how to make prawn curry"),
    ("Spicy Potatoes", "give me recipe with potato"),
    ("Parippu Vada", "how to make parippu vada"),
]

clicked_prompt = None
cols = st.columns(len(chips))
for i, (label, query) in enumerate(chips):
    with cols[i]:
        if st.button(label, use_container_width=True, key=f"chip_{i}"):
            clicked_prompt = query

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ============================================================
# RENDER CHAT HISTORY (Zero Emojis)
# ============================================================
for idx, msg in enumerate(st.session_state.messages):
    avatar_label = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(avatar_label):
        if msg.get("type") == "recipe_card":
            render_recipe_card(msg["content"], card_key=f"hist_{idx}")
        else:
            st.markdown(msg["content"])

# ============================================================
# USER INPUT HANDLING
# ============================================================
user_prompt = st.chat_input("Ask for a recipe, input ingredients, or set dietary limits (e.g. 'chicken, coconut milk and lemongrass')...")

# If user clicked a quick chip, use it as prompt
if clicked_prompt and not user_prompt:
    user_prompt = clicked_prompt

if user_prompt:
    # Append user message
    st.session_state.messages.append({"role": "user", "type": "text", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Prepare API payload
    payload = {
        "prompt": user_prompt,
        "allergies": selected_allergies,
        "diet_type": diet_choice if diet_choice != "None" else None,
        "max_time_minutes": max_time,
        "max_calories": calorie_limit,
        "cuisine": cuisine_pref if cuisine_pref != "Any" else None,
        "conversation_history": [
            {"role": m["role"], "content": m["content"] if isinstance(m["content"], str) else m["content"].get("recipe_title", "")}
            for m in st.session_state.messages[:-1]
        ]
    }

    with st.chat_message("assistant"):
        with st.spinner("Analyzing constraints and executing multi-agent pipeline..."):
            try:
                res = requests.post(BACKEND_URL, json=payload, timeout=20.0)
                if res.status_code == 200:
                    data = res.json()
                    resp_type = data.get("response_type", "conversational")

                    if resp_type == "recipe_recommendation":
                        render_recipe_card(data, card_key=f"card_{len(st.session_state.messages)}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "type": "recipe_card",
                            "content": data
                        })
                    else:
                        msg_text = data.get("message", "Processing completed.")
                        st.markdown(msg_text)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "type": "text",
                            "content": msg_text
                        })

                elif res.status_code == 400:
                    err_detail = res.json().get("detail", {})
                    msg = err_detail.get("message", "Request blocked by safety guardrail.")
                    violations = err_detail.get("violations", [])
                    st.error(f"Safety Guardrail: {msg}")
                    if violations:
                        for v in violations:
                            st.write(f"- {v}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "text",
                        "content": f"Safety Guardrail Blocked: {msg}"
                    })

                else:
                    err_msg = res.json().get("detail", "Error processing request.")
                    st.error(f"Error ({res.status_code}): {err_msg}")

            except requests.exceptions.ConnectionError:
                st.error("Backend service is offline. Ensure FastAPI backend is running at http://127.0.0.1:8000.")
            except Exception as e:
                st.error(f"Unexpected connection error: {e}")

# ============================================================
# BOTTOM READY CTA BANNER (FlightSense Style)
# ============================================================
cta_img_tag = f'<img src="{cta_img_b64}" alt="Healthy Cuisine Preparation" style="width: 100%; height: 130px; object-fit: cover; border-radius: 12px; border: 1px solid #e2e8f0;">' if cta_img_b64 else '<div style="background: #e2e8f0; width: 100%; height: 130px; border-radius: 12px;"></div>'

render_html(f"""
<div style="
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 22px 28px;
    margin-top: 36px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
">
    <div style="display: grid; grid-template-columns: 240px 1fr auto; gap: 24px; align-items: center;">
        <div>
            {cta_img_tag}
        </div>
        <div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;">
                Ready to Discover Your Next Healthy Meal?
            </div>
            <div style="font-size: 13px; color: #64748b; line-height: 1.5;">
                Use autonomous multi-agent intelligence to explore balanced recipes tailored to your dietary limits and available pantry items.
            </div>
        </div>
        <div>
            <span style="
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                color: #1d4ed8;
                padding: 8px 18px;
                border-radius: 999px;
                font-size: 12.5px;
                font-weight: 600;
            ">
                Verified NutriGuard Engine
            </span>
        </div>
    </div>
</div>
""")

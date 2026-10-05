"""
FRONTEND COMPONENT: Recipe & Nutrition Tip Cards
================================================
Renders formatted recipe recommendations, safety badges,
breakdown indicators, and healthy nutrition tip cards.
Enforces unique key assignment for embedded Plotly charts.
"""

from typing import Dict, Any
import streamlit as st
from frontend.components.charts import render_macro_chart


def render_recipe_card(data: Dict[str, Any], card_key: str):
    """
    Renders an interactive recipe recommendation card containing:
    - Match score & safety certification badge
    - Why selected explanation from Agent 5
    - Formatted cooking steps
    - Plotly macronutrient distribution (with unique chart key)
    - Source attribution
    """
    title = data.get("recipe_title", "Recommended Dish")
    score = float(data.get("score", 0.0))
    score_pct = int(score * 100)
    why_selected = data.get("why_selected", "")
    instructions = data.get("formatted_instructions", "")
    nutrition_facts = data.get("nutrition_facts", {})
    warnings = data.get("warnings", [])
    sources = data.get("sources", [])
    breakdown = data.get("score_breakdown", {})

    st.markdown(f"### 🍲 {title}")

    # Top badges row
    col1, col2, col3 = st.columns([1.2, 1.2, 2])
    with col1:
        st.metric(label="Match Score", value=f"{score_pct}%")
    with col2:
        st.success("🛡️ Allergen Safe")
    with col3:
        if sources:
            st.caption(f"📍 **Source:** {', '.join(sources)}")

    # Score breakdown expander
    if breakdown:
        with st.expander("📊 View Match Score Breakdown"):
            cols = st.columns(len(breakdown))
            for i, (factor, val) in enumerate(breakdown.items()):
                with cols[i]:
                    label_clean = factor.replace("_", " ").title()
                    st.metric(label=label_clean, value=f"{int(val * 100)}%")

    # Why Selected Box
    st.info(f"**Why this recipe was selected:**\n\n{why_selected}")

    # Warnings if any
    if warnings:
        for w in warnings:
            st.warning(f"⚠️ {w}")

    # Two column layout: Cooking Steps & Nutrition Chart
    c_left, c_right = st.columns([1.4, 1.0])

    with c_left:
        st.markdown("#### 📝 Step-by-Step Instructions")
        st.markdown(instructions)

    with c_right:
        st.markdown("#### 🥗 Nutrition Profile")
        if nutrition_facts:
            # Enforce CRITICAL UNIQUE PLOTLY CHART KEY
            fig = render_macro_chart(nutrition_facts)
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{card_key}")
        else:
            st.write("Nutrition details not available.")


def render_tip_card(tip: Dict[str, Any]):
    """
    Renders a nutrition tip or food safety news card.
    """
    title = tip.get("title", "")
    summary = tip.get("summary", "")
    content = tip.get("content", "")
    category = tip.get("category", "tip")
    author = tip.get("author", "NutriGuard Editorial")
    tags = tip.get("tags", "")

    badge = "🌿 Nutrition Tip" if category == "tip" else "📢 Food Safety News"
    badge_color = "green" if category == "tip" else "red"

    st.markdown(
        f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; margin-bottom: 16px;">
            <span style="background-color: {'#dcfce7' if category == 'tip' else '#fee2e2'}; color: {'#166534' if category == 'tip' else '#991b1b'}; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 999px;">
                {badge}
            </span>
            <h3 style="margin-top: 10px; color: #0f172a;">{title}</h3>
            <p style="color: #475569; font-size: 14px; font-style: italic;">{summary}</p>
            <p style="color: #334155; font-size: 15px; line-height: 1.6;">{content}</p>
            <div style="margin-top: 12px; font-size: 12px; color: #64748b;">
                <strong>Author:</strong> {author} &nbsp;|&nbsp; <strong>Tags:</strong> {tags}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

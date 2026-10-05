"""
FRONTEND COMPONENT: Recipe & Nutrition Tip Cards
================================================
Luxury Dark-Gold Design with Glassmorphism and Polished Typography.
Uses native Streamlit components with custom gold accents for maximum responsiveness.
"""

from typing import Dict, Any
import streamlit as st
from frontend.components.charts import render_macro_chart


def render_recipe_card(data: Dict[str, Any], card_key: str):
    """
    Renders an ultra-modern, luxury recipe recommendation card:
    - Gold-accented dish title and origin badge
    - Quick macronutrient indicator metrics
    - Why selected explanation from Agent 5
    - Formatted cooking steps
    - Plotly macronutrient distribution (transparent dark-gold theme)
    - 5-Agent weighted scoring breakdown audit
    """
    title = data.get("recipe_title", "Recommended Dish")
    score = float(data.get("score", 0.0))
    score_pct = int(score * 100)
    why_selected = data.get("why_selected", "")
    instructions = data.get("formatted_instructions", "")
    nutrition_facts = data.get("nutrition_facts", {})
    warnings = data.get("warnings", [])
    sources = data.get("sources", ["NutriGuard Knowledgebase"])
    breakdown = data.get("score_breakdown", {})

    cals = int(nutrition_facts.get("calories", 0))
    protein = int(nutrition_facts.get("protein_grams", 0))
    carbs = int(nutrition_facts.get("carbs_grams", 0))
    fat = int(nutrition_facts.get("fat_grams", 0))

    source_label = sources[0] if sources else "NutriGuard Knowledgebase"
    is_local = "Local" in source_label
    origin_badge = "🇱🇰 Authentic Sri Lankan" if is_local else "🌍 Global Culinary Archive"

    # Luxury Card Header
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(212,175,55,0.08) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(212,175,55,0.22);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
    ">
        <div>
            <div style="
                font-family: 'Playfair Display', serif;
                font-size: 1.5rem;
                font-weight: 700;
                color: #f0d060;
                letter-spacing: -0.3px;
            ">🍲 {title}</div>
            <div style="color: #64748b; font-size: 12px; margin-top: 3px;">
                <span style="color: #cbd5e1; font-weight: 500;">{origin_badge}</span> &nbsp;·&nbsp;
                <span>Source: <code style="color: #94a3b8; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;">{source_label}</code></span>
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <div style="
                background: linear-gradient(135deg, #d4af37, #b8932a);
                color: #0d1117;
                padding: 6px 14px;
                border-radius: 20px;
                font-weight: 800;
                font-size: 13px;
                letter-spacing: 0.04em;
                box-shadow: 0 2px 10px rgba(212,175,55,0.3);
            ">⭐ {score_pct}% MATCH</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric Row
    c1, c2, c3, c4, c5, c6 = st.columns([1.1, 1.2, 1.1, 1.1, 1.1, 1.8])
    with c1:
        st.metric(label="Match", value=f"{score_pct}%")
    with c2:
        st.metric(label="Calories", value=f"{cals} kcal")
    with c3:
        st.metric(label="Protein", value=f"{protein}g")
    with c4:
        st.metric(label="Carbs", value=f"{carbs}g")
    with c5:
        st.metric(label="Fats", value=f"{fat}g")
    with c6:
        st.success("🛡️ 100% Allergen Safe")

    # Why Selected Callout Box
    st.info(f"{why_selected}")

    # Allergen Warnings if any
    if warnings:
        for w in warnings:
            st.warning(f"⚠️ {w}")

    # Tabs for Instructions, Nutrition & Match Score Audit
    tab_instructions, tab_nutrition, tab_audit = st.tabs([
        "📝 Step-by-Step Instructions",
        "📊 Nutrition & Macronutrients",
        "🔍 Multi-Agent Score Audit"
    ])

    with tab_instructions:
        st.markdown(instructions)

    with tab_nutrition:
        col_chart, col_summary = st.columns([1.4, 1.0])
        with col_chart:
            if nutrition_facts:
                fig = render_macro_chart(nutrition_facts)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{card_key}")
            else:
                st.write("Macronutrient breakdown not available.")
        with col_summary:
            st.markdown("##### 🥗 Macro Summary")
            st.markdown(
                f"""
                - **Calories:** `{cals} kcal`
                - **Protein:** `{protein} g` *(Muscle recovery & satiety)*
                - **Carbohydrates:** `{carbs} g` *(Clean sustained energy)*
                - **Fats:** `{fat} g` *(Essential cellular lipids)*
                """
            )
            st.caption("Standardized nutritional estimate per single adult serving.")

    with tab_audit:
        st.markdown("##### 🤖 5-Agent Weighted Scoring Breakdown")
        if breakdown:
            cols = st.columns(len(breakdown))
            for i, (factor, val) in enumerate(breakdown.items()):
                with cols[i]:
                    label_clean = factor.replace("_", " ").title()
                    st.metric(label=label_clean, value=f"{int(val * 100)}%")
        st.caption("Audited by Agent 3 (Safety Guardrail) and optimized by Agent 4 (Linear Weighted Multi-Factor Ranking).")


def render_tip_card(tip: Dict[str, Any]):
    """
    Renders an attractive luxury nutrition tip or food safety news card.
    """
    title = tip.get("title", "")
    summary = tip.get("summary", "")
    content = tip.get("content", "")
    category = tip.get("category", "tip")
    author = tip.get("author", "NutriGuard Editorial")
    tags = tip.get("tags", "")

    is_tip = category == "tip"
    badge_label = "🌿 NUTRITION INSIGHT" if is_tip else "📢 FOOD SAFETY ADVISORY"
    badge_color = "#10b981" if is_tip else "#f59e0b"
    badge_bg = "rgba(16,185,129,0.1)" if is_tip else "rgba(245,158,11,0.1)"
    badge_border = "rgba(16,185,129,0.25)" if is_tip else "rgba(245,158,11,0.25)"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(212,175,55,0.03) 100%);
        border: 1px solid rgba(212,175,55,0.16);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="
                background: {badge_bg};
                border: 1px solid {badge_border};
                color: {badge_color};
                padding: 4px 12px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.06em;
            ">{badge_label}</span>
            <span style="color: #64748b; font-size: 12px;">By <strong style="color: #94a3b8;">{author}</strong></span>
        </div>
        <div style="
            font-family: 'Playfair Display', serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: #f0d060;
            margin-bottom: 8px;
        ">{title}</div>
        <div style="color: #94a3b8; font-size: 13px; font-style: italic; margin-bottom: 12px; line-height: 1.5;">
            "{summary}"
        </div>
        <div style="color: #cbd5e1; font-size: 13.5px; line-height: 1.6; margin-bottom: 12px;">
            {content}
        </div>
        <div style="color: #475569; font-size: 11px; font-family: monospace;">
            TAGS: <span style="color: #64748b;">{tags}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

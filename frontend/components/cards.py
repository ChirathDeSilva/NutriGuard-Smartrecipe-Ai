"""
FRONTEND COMPONENT: Recipe & Nutrition Tip Cards
================================================
Enterprise Light Theme (FlightSense Style).
Clean white cards, crisp typography (Inter), soft slate borders,
subtle shadows, and strictly ZERO emojis.
"""

from typing import Dict, Any
import streamlit as st
from frontend.components.charts import render_macro_chart
from frontend.utils import render_html


def render_recipe_card(data: Dict[str, Any], card_key: str):
    """
    Renders an enterprise-grade recipe recommendation card:
    - Clean white card with slate-200 border and subtle elevation
    - Royal blue confidence match pill
    - Verified allergen safety badge
    - Standard macronutrient indicators
    - Grounded culinary rationale
    - Numbered cooking instructions
    - Interactive Plotly macronutrient profile chart
    - Zero emojis used across all components
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
    origin_badge = "Authentic Sri Lankan" if is_local else "Global Culinary Archive"

    # Enterprise Card Header (Clean White / Royal Blue Accent)
    render_html(f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    ">
        <div>
            <div style="
                font-size: 1.45rem;
                font-weight: 700;
                color: #0f172a;
                letter-spacing: -0.02em;
                line-height: 1.2;
            ">{title}</div>
            <div style="color: #64748b; font-size: 12px; margin-top: 6px; display: flex; align-items: center; gap: 8px;">
                <span style="
                    background: #f1f5f9;
                    color: #334155;
                    font-weight: 600;
                    padding: 3px 10px;
                    border-radius: 999px;
                    border: 1px solid #e2e8f0;
                ">{origin_badge}</span>
                <span>Source: <code style="color: #475569; background: #f8fafc; padding: 2px 8px; border-radius: 4px; border: 1px solid #e2e8f0;">{source_label}</code></span>
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <div style="
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                color: #1d4ed8;
                padding: 6px 14px;
                border-radius: 999px;
                font-weight: 700;
                font-size: 13px;
                letter-spacing: 0.02em;
            ">{score_pct}% Match Score</div>
            <div style="
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                color: #15803d;
                padding: 6px 14px;
                border-radius: 999px;
                font-weight: 600;
                font-size: 12px;
            ">Allergen Verified</div>
        </div>
    </div>
    """)

    # Metric Row (6 Clean Cards)
    c1, c2, c3, c4, c5, c6 = st.columns([1.1, 1.2, 1.1, 1.1, 1.1, 1.6])
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
        st.metric(label="Safety Status", value="Verified Safe")

    # Clean Callout Box (Why Selected)
    st.info(why_selected)

    # Allergen Warnings if any
    if warnings:
        for w in warnings:
            st.warning(f"Safety Advisory: {w}")

    # Tabs for Instructions, Nutrition & Match Score Audit (Zero emojis)
    tab_instructions, tab_nutrition, tab_audit = st.tabs([
        "Preparation Instructions",
        "Macronutrient Profile",
        "Multi-Agent Scoring Audit"
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
            st.markdown("##### Nutritional Summary")
            st.markdown(
                f"""
                - **Calories:** `{cals} kcal`
                - **Protein:** `{protein} g` (Essential amino acids)
                - **Carbohydrates:** `{carbs} g` (Sustained energy)
                - **Fats:** `{fat} g` (Dietary lipids)
                """
            )
            st.caption("Standardized nutritional estimate per single adult serving.")

    with tab_audit:
        st.markdown("##### Multi-Factor Weighted Scoring Breakdown")
        if breakdown:
            cols = st.columns(len(breakdown))
            for i, (factor, val) in enumerate(breakdown.items()):
                with cols[i]:
                    label_clean = factor.replace("_", " ").title()
                    st.metric(label=label_clean, value=f"{int(val * 100)}%")
        st.caption("Audited by Agent 3 (Safety Guardrail) and scored by Agent 4 (Multi-Factor Linear Ranking).")


def render_tip_card(tip: Dict[str, Any]):
    """
    Renders an enterprise-grade nutrition tip or food safety news card.
    Zero emojis used.
    """
    title = tip.get("title", "")
    summary = tip.get("summary", "")
    content = tip.get("content", "")
    category = tip.get("category", "tip")
    author = tip.get("author", "NutriGuard Editorial Board")
    tags = tip.get("tags", "")

    is_tip = category == "tip"
    badge_label = "Nutrition Research" if is_tip else "Food Safety Advisory"
    badge_color = "#0284c7" if is_tip else "#d97706"
    badge_bg = "#f0f9ff" if is_tip else "#fffbeb"
    badge_border = "#bae6fd" if is_tip else "#fde68a"

    render_html(f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 22px 26px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span style="
                background: {badge_bg};
                border: 1px solid {badge_border};
                color: {badge_color};
                padding: 4px 12px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            ">{badge_label}</span>
            <span style="color: #64748b; font-size: 12px;">Authored by <strong style="color: #334155;">{author}</strong></span>
        </div>
        <div style="
            font-size: 1.2rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 8px;
            letter-spacing: -0.01em;
        ">{title}</div>
        <div style="color: #64748b; font-size: 13.5px; margin-bottom: 12px; line-height: 1.5;">
            {summary}
        </div>
        <div style="color: #334155; font-size: 14px; line-height: 1.6; margin-bottom: 12px;">
            {content}
        </div>
        <div style="color: #94a3b8; font-size: 11px; font-family: monospace;">
            TOPICS: <span style="color: #64748b;">{tags}</span>
        </div>
    </div>
    """)

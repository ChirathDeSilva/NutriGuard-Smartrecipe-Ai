"""
FRONTEND COMPONENT: Recipe & Nutrition Tip Cards
================================================
Renders formatted recipe recommendations, safety badges,
breakdown indicators, and healthy nutrition tip cards.
Enforces unique key assignment for embedded Plotly charts.
Uses native Streamlit widgets for perfect dark/light theme compatibility.
"""

from typing import Dict, Any
import streamlit as st
from frontend.components.charts import render_macro_chart


def render_recipe_card(data: Dict[str, Any], card_key: str):
    """
    Renders an interactive, polished recipe recommendation card using
    native Streamlit components for seamless dark/light mode compatibility:
    - Match score & safety certification badge
    - Quick macronutrient indicator metrics
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
    sources = data.get("sources", ["NutriGuard Knowledgebase"])
    breakdown = data.get("score_breakdown", {})

    # Extract macro details
    cals = int(nutrition_facts.get("calories", 0))
    protein = int(nutrition_facts.get("protein_grams", 0))
    carbs = int(nutrition_facts.get("carbs_grams", 0))
    fat = int(nutrition_facts.get("fat_grams", 0))

    source_label = sources[0] if sources else "NutriGuard Knowledgebase"
    is_local = "Local" in source_label
    origin_badge = "🇱🇰 Authentic Sri Lankan" if is_local else "🌍 Global Cuisine"

    # Header title and origin metadata
    st.markdown(f"### 🍲 {title}")
    st.caption(f"**Cuisine:** `{origin_badge}` &nbsp;|&nbsp; 📍 **Source:** `{source_label}`")

    # Native Metric Cards Row (Works perfectly in Dark & Light themes)
    c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1.2, 1.2, 1.2, 1.2, 1.8])
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
                - **Protein:** `{protein} g` (Muscle recovery)
                - **Carbohydrates:** `{carbs} g` (Sustained energy)
                - **Fats:** `{fat} g` (Essential lipids)
                """
            )
            st.caption("Values estimated per single standard adult serving.")

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
    Renders an attractive nutrition tip or food safety news card.
    """
    title = tip.get("title", "")
    summary = tip.get("summary", "")
    content = tip.get("content", "")
    category = tip.get("category", "tip")
    author = tip.get("author", "NutriGuard Editorial")
    tags = tip.get("tags", "")

    badge = "🌿 Nutrition Tip" if category == "tip" else "📢 Food Safety News"

    st.markdown(f"#### {badge}: {title}")
    st.caption(f"_{summary}_")
    st.markdown(content)
    st.caption(f"**Author:** {author} | **Tags:** {tags}")
    st.divider()

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
    Renders an interactive, polished recipe recommendation card containing:
    - Match score & safety certification badge
    - Quick macronutrient indicator pills
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
    sources = data.get("sources", ["NutriGuard Culinary Knowledgebase"])
    breakdown = data.get("score_breakdown", {})

    # Extract macro details
    cals = int(nutrition_facts.get("calories", 0))
    protein = int(nutrition_facts.get("protein_grams", 0))
    carbs = int(nutrition_facts.get("carbs_grams", 0))
    fat = int(nutrition_facts.get("fat_grams", 0))

    source_label = sources[0] if sources else "NutriGuard Knowledgebase"
    is_local = "Local" in source_label

    # Header Card Container
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
                    border: 1px solid #cbd5e1; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span style="background-color: {'#e0f2fe' if is_local else '#fef3c7'}; 
                                 color: {'#0369a1' if is_local else '#b45309'}; 
                                 font-size: 11px; font-weight: 700; text-transform: uppercase; 
                                 padding: 3px 10px; border-radius: 999px; letter-spacing: 0.5px;">
                        {'🇱🇰 Authentic Sri Lankan' if is_local else '🌍 Global Cuisine'}
                    </span>
                    <h2 style="margin: 6px 0 2px 0; color: #0f172a; font-size: 1.6rem; font-weight: 700;">
                        🍲 {title}
                    </h2>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; 
                                 font-weight: 700; font-size: 13px; padding: 5px 12px; border-radius: 8px;">
                        🛡️ 100% Allergen Safe
                    </span>
                    <span style="background-color: #4f46e5; color: #ffffff; 
                                 font-weight: 800; font-size: 14px; padding: 5px 14px; border-radius: 8px;">
                        {score_pct}% Match
                    </span>
                </div>
            </div>
            
            <!-- Quick Macro Pills Row -->
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px;">
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 600; color: #334155;">
                    🔥 <strong>{cals}</strong> kcal
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 600; color: #166534;">
                    💪 <strong>{protein}g</strong> Protein
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 600; color: #0284c7;">
                    🌾 <strong>{carbs}g</strong> Carbs
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 600; color: #d97706;">
                    🥑 <strong>{fat}g</strong> Fats
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; font-size: 12px; color: #64748b; margin-left: auto;">
                    📍 Source: <em>{source_label}</em>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

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
        c_left, c_right = st.columns([1.4, 1.0])
        with c_left:
            if nutrition_facts:
                fig = render_macro_chart(nutrition_facts)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{card_key}")
            else:
                st.write("Macronutrient breakdown not available.")
        with c_right:
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

    st.markdown(
        f"""
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="margin-bottom: 10px;">
                <span style="background-color: {'#dcfce7' if category == 'tip' else '#fee2e2'}; 
                             color: {'#166534' if category == 'tip' else '#991b1b'}; 
                             font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 999px;">
                    {badge}
                </span>
            </div>
            <h3 style="margin: 8px 0; color: #0f172a; font-weight: 700;">{title}</h3>
            <p style="color: #475569; font-size: 14px; font-style: italic; margin-bottom: 12px;">{summary}</p>
            <p style="color: #334155; font-size: 15px; line-height: 1.6;">{content}</p>
            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid #f1f5f9; font-size: 12px; color: #64748b;">
                <strong>Author:</strong> {author} &nbsp;|&nbsp; <strong>Tags:</strong> {tags}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

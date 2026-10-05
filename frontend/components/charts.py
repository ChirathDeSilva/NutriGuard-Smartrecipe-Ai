"""
FRONTEND COMPONENT: Plotly Horizontal Macronutrient Chart
=========================================================
Ultra-Modern Luxury Dark-Gold Theme Plotly Chart
Seamlessly matches high-end dark glassmorphic UI.
"""

from typing import Dict, Any
import plotly.graph_objects as go


def render_macro_chart(nutrition_facts: Dict[str, Any]) -> go.Figure:
    """
    Constructs a horizontal Plotly bar chart displaying the macronutrient distribution:
    Protein, Carbohydrates, and Fats in grams with an expensive dark luxury aesthetic.
    """
    protein = float(nutrition_facts.get("protein_grams", 0.0))
    carbs = float(nutrition_facts.get("carbs_grams", 0.0))
    fat = float(nutrition_facts.get("fat_grams", 0.0))
    calories = float(nutrition_facts.get("calories", 0.0))

    categories = ["Protein", "Carbs", "Fat"]
    values = [protein, carbs, fat]
    colors = ["#10b981", "#38bdf8", "#f59e0b"]  # Emerald, Sapphire, Gold

    fig = go.Figure(
        go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255, 255, 255, 0.15)", width=1.5),
                cornerradius=6
            ),
            text=[f"  <b>{v:.0f}g</b>" for v in values],
            textposition="inside",
            insidetextanchor="start",
            insidetextfont=dict(color="#ffffff", size=12, family="Inter, sans-serif"),
            hoverinfo="x+y"
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Macronutrient Distribution</b> · <span style='color:#f0d060;'>{calories:.0f} kcal</span>",
            font=dict(size=14, color="#e8ecf4", family="Inter, sans-serif"),
            x=0.02,
            y=0.92
        ),
        xaxis=dict(
            title=dict(
                text="Grams per Serving",
                font=dict(color="#64748b", size=11, family="Inter, sans-serif")
            ),
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.06)",
            tickfont=dict(color="#94a3b8", size=11),
            zeroline=False
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#e2e8f0", size=12, family="Inter, sans-serif")
        ),
        margin=dict(l=10, r=20, t=35, b=25),
        height=200,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        bargap=0.35
    )

    return fig

"""
FRONTEND COMPONENT: Plotly Horizontal Macronutrient Chart
=========================================================
Renders horizontal bar charts representing Calories, Protein, Carbs, and Fats.
"""

from typing import Dict, Any
import plotly.graph_objects as go


def render_macro_chart(nutrition_facts: Dict[str, Any]) -> go.Figure:
    """
    Constructs a horizontal Plotly bar chart displaying the macronutrient distribution:
    Protein, Carbohydrates, and Fats in grams.
    """
    protein = float(nutrition_facts.get("protein_grams", 0.0))
    carbs = float(nutrition_facts.get("carbs_grams", 0.0))
    fat = float(nutrition_facts.get("fat_grams", 0.0))
    calories = float(nutrition_facts.get("calories", 0.0))

    categories = ["Protein (g)", "Carbs (g)", "Fat (g)"]
    values = [protein, carbs, fat]
    colors = ["#2ecc71", "#3498db", "#e67e22"]  # Green, Blue, Orange

    fig = go.Figure(
        go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="#2c3e50", width=1.5)
            ),
            text=[f"{v}g" for v in values],
            textposition="auto",
        )
    )

    fig.update_layout(
        title=dict(
            text=f"Macronutrient Profile (Total: {calories:.0f} kcal)",
            font=dict(size=14, color="#1e293b")
        ),
        xaxis=dict(
            title="Grams per Serving",
            showgrid=True,
            gridcolor="#e2e8f0"
        ),
        yaxis=dict(
            autorange="reversed"
        ),
        margin=dict(l=20, r=20, t=35, b=25),
        height=220,
        plot_bgcolor="#f8fafc",
        paper_bgcolor="#ffffff"
    )

    return fig

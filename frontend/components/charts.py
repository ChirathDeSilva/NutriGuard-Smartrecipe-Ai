"""
FRONTEND COMPONENT: Plotly Horizontal Macronutrient Chart
=========================================================
Clean Enterprise Light Theme (FlightSense Style).
Features crisp royal blue, teal, and amber palette with zero emojis.
"""

from typing import Dict, Any
import plotly.graph_objects as go


def render_macro_chart(nutrition_facts: Dict[str, Any]) -> go.Figure:
    """
    Constructs a horizontal Plotly bar chart displaying the macronutrient distribution:
    Protein, Carbohydrates, and Fats in grams using a clean enterprise light aesthetic.
    """
    protein = float(nutrition_facts.get("protein_grams", 0.0))
    carbs = float(nutrition_facts.get("carbs_grams", 0.0))
    fat = float(nutrition_facts.get("fat_grams", 0.0))
    calories = float(nutrition_facts.get("calories", 0.0))

    categories = ["Protein", "Carbohydrates", "Fats"]
    values = [protein, carbs, fat]
    colors = ["#2563eb", "#0d9488", "#d97706"]  # Royal Blue, Teal, Amber

    fig = go.Figure(
        go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(0, 0, 0, 0.04)", width=1),
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
            text=f"<b style='color:#0f172a; font-size:14px;'>Macronutrient Distribution</b> · <span style='color:#2563eb; font-weight:600;'>{calories:.0f} kcal total</span>",
            font=dict(size=14, color="#0f172a", family="Inter, sans-serif"),
            x=0.01,
            y=0.92
        ),
        xaxis=dict(
            title=dict(
                text="Grams per Adult Serving",
                font=dict(color="#64748b", size=11, family="Inter, sans-serif")
            ),
            showgrid=True,
            gridcolor="#f1f5f9",
            tickfont=dict(color="#64748b", size=11, family="Inter, sans-serif"),
            zeroline=False
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#1e293b", size=12, family="Inter, sans-serif")
        ),
        margin=dict(l=10, r=20, t=35, b=25),
        height=200,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        bargap=0.35
    )

    return fig

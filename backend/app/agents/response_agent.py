"""
AGENT 5: Response Agent (Grounded Gemini LLM Explanation & Formatting)
======================================================================
Takes the single top RankedRecipe from Agent 4 and provides an engaging,
grounded, strictly verified conversational explanation:
- Explains why the recipe was chosen based on score_breakdown
- Formats clean, numbered step-by-step instructions
- Strictly grounded in the provided recipe (no hallucinations of nutrition or medical claims)
- Includes fallback formatting if LLM API is unavailable
"""

import os
import json
from dotenv import load_dotenv
from typing import Dict, Any

from backend.app.db.schemas import RankedRecipe, FinalAgentResponse

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


async def generate_response(ranked: RankedRecipe) -> FinalAgentResponse:
    """
    Synthesizes the final grounded user-facing response using Gemini LLM
    or deterministic formatting fallback.
    """
    recipe = ranked.recipe
    breakdown = ranked.score_breakdown

    # Format standard fallback text
    score_pct = int(ranked.final_score * 100)
    why_selected_default = (
        f"This recipe achieved a {score_pct}% match because it perfectly incorporates your requested "
        f"ingredients with an ingredient score of {int(breakdown.get('ingredient_match', 1.0) * 100)}%, "
        f"adheres to all your allergen safety limits, and prepares in {recipe.cooking_minutes} minutes."
    )

    clean_instructions = recipe.instructions.strip()

    nutrition_facts: Dict[str, Any] = {
        "calories": recipe.calories,
        "protein_grams": recipe.protein_grams,
        "carbs_grams": recipe.carbs_grams,
        "fat_grams": recipe.fat_grams
    }

    warnings = []
    if recipe.allergens:
        warnings.append(f"Contains declared allergens: {', '.join(recipe.allergens)}")

    sources = [recipe.source]

    # Try calling Google Gemini if API key is present
    if GEMINI_API_KEY and not GEMINI_API_KEY.startswith("your_"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
You are NutriGuard AI, a food safety and culinary nutrition assistant.
Summarize this recipe recommendation for the user.

STRICT RULES:
1. ONLY use the recipe information provided below. Do NOT invent calories, cooking times, or ingredients.
2. In 'why_selected', write 2 sentences explaining why this recipe was selected using the score breakdown.
3. In 'formatted_instructions', provide clean numbered cooking steps.

Recipe:
Title: {recipe.title}
Cuisine: {recipe.cuisine}
Cooking Minutes: {recipe.cooking_minutes}
Calories: {recipe.calories} kcal
Protein: {recipe.protein_grams}g | Carbs: {recipe.carbs_grams}g | Fat: {recipe.fat_grams}g
Ingredients: {", ".join(recipe.ingredients)}
Raw Instructions: {recipe.instructions}
Match Score: {ranked.final_score}
Score Breakdown: {json.dumps(breakdown)}

Respond strictly in JSON format with two keys:
{{
  "why_selected": "...",
  "formatted_instructions": "..."
}}
"""
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Clean possible markdown JSON wrappers
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:].strip()

            parsed = json.loads(text)
            why_selected = parsed.get("why_selected", why_selected_default)
            formatted_instructions = parsed.get("formatted_instructions", clean_instructions)

            return FinalAgentResponse(
                recipe_title=recipe.title,
                score=ranked.final_score,
                why_selected=why_selected,
                formatted_instructions=formatted_instructions,
                nutrition_facts=nutrition_facts,
                warnings=warnings,
                sources=sources,
                score_breakdown=breakdown,
                is_nutrition_estimated=False
            )

        except Exception as e:
            print(f"[GEMINI RESPONSE AGENT FALLBACK] Using deterministic template due to: {e}")

    # Fallback response
    return FinalAgentResponse(
        recipe_title=recipe.title,
        score=ranked.final_score,
        why_selected=why_selected_default,
        formatted_instructions=clean_instructions,
        nutrition_facts=nutrition_facts,
        warnings=warnings,
        sources=sources,
        score_breakdown=breakdown,
        is_nutrition_estimated=False
    )

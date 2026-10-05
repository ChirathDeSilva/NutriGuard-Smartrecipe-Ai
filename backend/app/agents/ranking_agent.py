"""
AGENT 4: Ranking Agent (Linear Weighted Multi-Factor Scoring Formula)
====================================================================
Calculates a deterministic composite match score between user constraints and
safe candidate recipes using the project formula:

Score = 0.30 * (ingredient_match) +
        0.20 * (diet_match) +
        0.20 * (nutrition_match) +
        0.15 * (time_match) +
        0.10 * (cuisine_match) +
        0.05 * (popularity)
"""

from typing import List, Optional, Dict
from backend.app.db.schemas import CandidateRecipe, StructuredConstraints, RankedRecipe


def calculate_ingredient_match(recipe_ingredients: List[str], available_ingredients: List[str], recipe_title: str = "") -> float:
    """
    Computes fraction of available ingredients / dish search terms that appear
    in either the recipe ingredients or the recipe title.
    Returns value between 0.0 and 1.0.
    """
    if not available_ingredients:
        return 0.5  # Neutral baseline when user didn't specify ingredient restrictions

    matched = 0
    recipe_text = (" ".join(recipe_ingredients) + " " + recipe_title).lower()
    for ing in available_ingredients:
        ing_clean = ing.strip().lower()
        if not ing_clean:
            continue
        # Direct match or singular/plural stem match
        singular = ing_clean[:-1] if ing_clean.endswith("s") and len(ing_clean) > 3 else ing_clean
        if ing_clean in recipe_text or (singular and singular in recipe_text):
            matched += 1

    return min(1.0, matched / max(1, len(available_ingredients)))


def calculate_diet_match(recipe_tags: List[str], requested_diet: Optional[str]) -> float:
    """
    Checks if the recipe explicitly satisfies the user's dietary tag.
    Returns 1.0 if satisfied or not specified, else 0.5 default.
    """
    if not requested_diet:
        return 1.0

    req_lower = requested_diet.strip().lower()
    tags_lower = [t.lower() for t in recipe_tags]
    if req_lower in tags_lower:
        return 1.0
    return 0.8  # Safe candidates already passed strict safety agent filtering


def calculate_nutrition_match(recipe_calories: float, max_calories: Optional[float]) -> float:
    """
    Calculates proximity to the user's target or maximum calorie limit.
    Returns value between 0.0 and 1.0.
    """
    if not max_calories or max_calories <= 0:
        return 1.0

    # Since candidate is already verified <= max_calories by Agent 3:
    # A recipe comfortably within calorie limit gets higher score
    ratio = recipe_calories / max_calories
    if ratio <= 1.0:
        return 0.7 + (0.3 * ratio)  # Scale between 0.7 and 1.0
    return max(0.0, 1.0 - (ratio - 1.0))


def calculate_time_match(recipe_minutes: int, max_time: Optional[int]) -> float:
    """
    Calculates time alignment. Recipes faster than user maximum get high score.
    Returns value between 0.0 and 1.0.
    """
    if not max_time or max_time <= 0:
        return 1.0

    if recipe_minutes <= max_time:
        # Perfectly on or under time limit
        return 1.0
    else:
        # Slight penalty for exceeding preparation time
        overtime_ratio = (recipe_minutes - max_time) / max_time
        return max(0.0, 1.0 - overtime_ratio)


def calculate_cuisine_match(recipe_cuisine: str, requested_cuisine: Optional[str]) -> float:
    """
    Calculates cuisine match score.
    Returns 1.0 if match or not requested, 0.4 if different cuisine.
    """
    if not requested_cuisine:
        return 1.0

    if requested_cuisine.strip().lower() in recipe_cuisine.lower():
        return 1.0
    return 0.4


def rank(safe_recipes: List[CandidateRecipe], constraints: StructuredConstraints) -> Optional[RankedRecipe]:
    """
    Scores all safe recipes using the weighted linear formula and returns the
    single highest-ranking RankedRecipe.

    Returns:
        Top RankedRecipe or None if safe_recipes list is empty.
    """
    if not safe_recipes:
        return None

    scored_recipes: List[RankedRecipe] = []

    for recipe in safe_recipes:
        ing_score = calculate_ingredient_match(recipe.ingredients, constraints.available_ingredients, recipe.title)
        diet_score = calculate_diet_match(recipe.dietary_tags, constraints.diet_type)
        nutr_score = calculate_nutrition_match(recipe.calories, constraints.max_calories)
        time_score = calculate_time_match(recipe.cooking_minutes, constraints.max_time_minutes)
        cuis_score = calculate_cuisine_match(recipe.cuisine, constraints.cuisine)
        pop_score = max(0.0, min(1.0, recipe.popularity))

        final_score = (
            0.30 * ing_score +
            0.20 * diet_score +
            0.20 * nutr_score +
            0.15 * time_score +
            0.10 * cuis_score +
            0.05 * pop_score
        )

        breakdown: Dict[str, float] = {
            "ingredient_match": round(ing_score, 2),
            "diet_match": round(diet_score, 2),
            "nutrition_match": round(nutr_score, 2),
            "time_match": round(time_score, 2),
            "cuisine_match": round(cuis_score, 2),
            "popularity": round(pop_score, 2),
        }

        scored_recipes.append(
            RankedRecipe(
                recipe=recipe,
                final_score=round(final_score, 4),
                score_breakdown=breakdown
            )
        )

    # Sort descending by final score
    scored_recipes.sort(key=lambda r: r.final_score, reverse=True)
    return scored_recipes[0]

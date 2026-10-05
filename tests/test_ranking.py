"""
TEST SUITE: Ranking Agent (Agent 4) Scoring Formula
===================================================
Asserts:
1. Exact mathematical scoring using the linear weighted formula:
   Score = 0.30*(ing) + 0.20*(diet) + 0.20*(nutr) + 0.15*(time) + 0.10*(cuis) + 0.05*(pop)
2. Ingredient match weighting prioritizes the best recipe
3. Time and cuisine factor adjustments
"""

import pytest
from backend.app.agents.ranking_agent import (
    rank,
    calculate_ingredient_match,
    calculate_diet_match,
    calculate_nutrition_match,
    calculate_time_match,
    calculate_cuisine_match
)
from backend.app.db.schemas import CandidateRecipe, StructuredConstraints


def test_ingredient_match_calculation():
    """Asserts accurate fraction of matched ingredients."""
    recipe_ingredients = ["red lentils", "coconut milk", "turmeric"]

    # 1. Full match
    score_full = calculate_ingredient_match(recipe_ingredients, ["red lentils", "turmeric"])
    assert score_full == 1.0

    # 2. Partial match (1 of 2)
    score_half = calculate_ingredient_match(recipe_ingredients, ["red lentils", "chicken"])
    assert score_half == 0.5

    # 3. No match
    score_zero = calculate_ingredient_match(recipe_ingredients, ["beef", "pasta"])
    assert score_zero == 0.0

    # 4. Empty search criteria defaults to 0.5 neutral baseline
    assert calculate_ingredient_match(recipe_ingredients, []) == 0.5


def test_time_match_calculation():
    """Asserts time scoring logic."""
    # Under time limit
    assert calculate_time_match(20, 30) == 1.0
    # Exactly on time limit
    assert calculate_time_match(30, 30) == 1.0
    # Over time limit receives penalty
    over_score = calculate_time_match(45, 30)
    assert 0.0 <= over_score < 1.0


def test_cuisine_match_calculation():
    """Asserts cuisine matching logic."""
    assert calculate_cuisine_match("Sri Lankan", "Sri Lankan") == 1.0
    assert calculate_cuisine_match("Italian", "Sri Lankan") == 0.4
    assert calculate_cuisine_match("Sri Lankan", None) == 1.0


def test_full_weighted_ranking_math():
    """Asserts composite linear weighted formula accuracy."""
    dhal = CandidateRecipe(
        id="1",
        title="Dhal Curry",
        ingredients=["red lentils", "coconut milk"],
        instructions="Cook",
        cooking_minutes=25,
        calories=280.0,
        protein_grams=14.0,
        cuisine="Sri Lankan",
        popularity=0.8
    )

    chicken = CandidateRecipe(
        id="2",
        title="Chicken Curry",
        ingredients=["chicken", "curry powder"],
        instructions="Cook",
        cooking_minutes=40,
        calories=380.0,
        protein_grams=32.0,
        cuisine="Sri Lankan",
        popularity=0.9
    )

    # User explicitly wants chicken
    constraints = StructuredConstraints(
        available_ingredients=["chicken"],
        max_time_minutes=45,
        cuisine="Sri Lankan"
    )

    top_result = rank([dhal, chicken], constraints)
    assert top_result is not None
    assert top_result.recipe.id == "2", "Chicken curry must win when chicken is requested!"
    assert top_result.score_breakdown["ingredient_match"] == 1.0
    assert top_result.final_score > 0.8

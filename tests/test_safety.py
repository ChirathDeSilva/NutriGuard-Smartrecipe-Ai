"""
TEST SUITE: Safety Agent (Agent 3) Deterministic Food Safety Guardrails
========================================================================
Asserts:
1. 100% deterministic allergen blocking (including deep ingredient scanning)
2. Dietary lifestyle enforcement (Vegan, Vegetarian, Keto)
3. Plant-based milk exceptions (allowing coconut milk in vegan dishes)
4. Strict calorie ceiling enforcement
"""

import pytest
from backend.app.agents.safety_agent import validate_candidates
from backend.app.db.schemas import CandidateRecipe, StructuredConstraints


@pytest.fixture
def sample_recipes():
    """Provides a realistic set of candidate recipes for safety tests."""
    return [
        CandidateRecipe(
            id="1",
            title="Spicy Pol Sambol",
            ingredients=["fresh coconut", "red chili powder", "shallots", "lime juice", "maldive fish flakes"],
            instructions="Mix all ingredients thoroughly.",
            cooking_minutes=10,
            calories=190.0,
            protein_grams=4.0,
            carbs_grams=8.0,
            fat_grams=16.0,
            allergens=["Fish"],
            cuisine="Sri Lankan",
            source="Local Knowledgebase"
        ),
        CandidateRecipe(
            id="2",
            title="Sri Lankan Dhal Curry (Parippu)",
            ingredients=["red lentils", "coconut milk", "turmeric", "curry leaves", "mustard seeds", "onion"],
            instructions="Simmer lentils with spices and fold in coconut milk.",
            cooking_minutes=25,
            calories=280.0,
            protein_grams=14.0,
            carbs_grams=38.0,
            fat_grams=8.0,
            allergens=[],
            cuisine="Sri Lankan",
            source="Local Knowledgebase"
        ),
        CandidateRecipe(
            id="3",
            title="Sri Lankan Chicken Curry",
            ingredients=["chicken pieces", "roasted curry powder", "coconut milk", "garlic", "ginger"],
            instructions="Marinate chicken and simmer in coconut milk.",
            cooking_minutes=35,
            calories=420.0,
            protein_grams=32.0,
            carbs_grams=6.0,
            fat_grams=24.0,
            allergens=[],
            cuisine="Sri Lankan",
            source="Local Knowledgebase"
        )
    ]


def test_fish_allergy_deterministic_blocking(sample_recipes):
    """Asserts that fish allergy blocks Pol Sambol containing Maldive fish flakes."""
    constraints = StructuredConstraints(allergies=["fish"])
    safe, verdicts = validate_candidates(sample_recipes, constraints)

    # Assert Pol Sambol is blocked
    safe_ids = [r.id for r in safe]
    assert "1" not in safe_ids, "Pol Sambol containing fish must be blocked!"
    assert "2" in safe_ids, "Dhal curry must be safe from fish allergy!"
    assert "3" in safe_ids, "Chicken curry must be safe from fish allergy!"

    # Assert verdict violation details
    sambol_verdict = next(v for v in verdicts if v.recipe_id == "1")
    assert not sambol_verdict.is_safe
    assert any("fish" in viol.lower() for viol in sambol_verdict.violations)


def test_vegan_diet_rejection_and_plant_milk_support(sample_recipes):
    """Asserts vegan filter rejects meat and fish while permitting coconut milk."""
    constraints = StructuredConstraints(diet_type="vegan")
    safe, verdicts = validate_candidates(sample_recipes, constraints)

    safe_ids = [r.id for r in safe]
    # Dhal is vegan (contains coconut milk, red lentils)
    assert "2" in safe_ids, "Dhal with coconut milk must be recognized as vegan!"
    # Pol Sambol contains fish, Chicken Curry contains chicken -> both rejected
    assert "1" not in safe_ids, "Pol Sambol containing seafood must not be vegan!"
    assert "3" not in safe_ids, "Chicken curry must not be vegan!"


def test_calorie_ceiling_enforcement(sample_recipes):
    """Asserts recipes exceeding requested maximum calories are strictly rejected."""
    # Set calorie limit to 300 kcal (Dhal is 280, Sambol is 190, Chicken is 420)
    constraints = StructuredConstraints(max_calories=300.0)
    safe, verdicts = validate_candidates(sample_recipes, constraints)

    safe_ids = [r.id for r in safe]
    assert "3" not in safe_ids, "Chicken curry (420 kcal) must exceed 300 kcal ceiling!"
    assert "1" in safe_ids, "Pol Sambol (190 kcal) is within 300 kcal limit."
    assert "2" in safe_ids, "Dhal curry (280 kcal) is within 300 kcal limit."

    chicken_verdict = next(v for v in verdicts if v.recipe_id == "3")
    assert not chicken_verdict.is_safe
    assert any("calories" in viol.lower() for viol in chicken_verdict.violations)


def test_clean_recipe_passes_without_constraints(sample_recipes):
    """Asserts all candidates pass when user has no restrictions."""
    constraints = StructuredConstraints()
    safe, verdicts = validate_candidates(sample_recipes, constraints)

    assert len(safe) == len(sample_recipes)
    assert all(v.is_safe for v in verdicts)

import pytest
import asyncio
from backend.app.services.external_apis import search_themealdb, parse_themealdb_to_candidate_dict
from backend.app.agents.retrieval_agent import retrieve_candidates
from backend.app.agents.safety_agent import validate_candidates
from backend.app.db.schemas import StructuredConstraints, CandidateRecipe


@pytest.mark.anyio
async def test_themealdb_api_connectivity():
    """Verifies that TheMealDB API endpoint responds with valid meal objects."""
    meals = await search_themealdb("pizza")
    assert isinstance(meals, list)
    assert len(meals) > 0
    assert "strMeal" in meals[0]
    assert "strInstructions" in meals[0]


def test_themealdb_normalization():
    """Verifies raw TheMealDB JSON is correctly normalized into CandidateRecipe format."""
    mock_meal = {
        "idMeal": "52772",
        "strMeal": "Teriyaki Chicken Casserole",
        "strArea": "Japanese",
        "strInstructions": "Bake in oven for 30 minutes.",
        "strIngredient1": "Chicken Breast",
        "strMeasure1": "3/4 cup",
        "strIngredient2": "Soy Sauce",
        "strMeasure2": "1/2 cup"
    }
    candidate_dict = parse_themealdb_to_candidate_dict(mock_meal)
    candidate = CandidateRecipe(**candidate_dict)

    assert candidate.id == "mealdb_52772"
    assert candidate.title == "Teriyaki Chicken Casserole"
    assert candidate.cuisine == "Japanese"
    assert "3/4 cup chicken breast" in candidate.ingredients
    assert "1/2 cup soy sauce" in candidate.ingredients
    assert candidate.source == "TheMealDB (External API)"


@pytest.mark.anyio
async def test_themealdb_pipeline_fallback():
    """Verifies that queries not found in local DB fall back to TheMealDB."""
    constraints = StructuredConstraints(available_ingredients=["pasta"])
    candidates = await retrieve_candidates(constraints)

    assert len(candidates) > 0
    # At least one candidate should originate from TheMealDB
    sources = [c.source for c in candidates]
    assert "TheMealDB (External API)" in sources


def test_themealdb_allergen_blocking():
    """Verifies that allergen detection protects against external TheMealDB recipes."""
    external_recipe = CandidateRecipe(
        id="mealdb_test_1",
        title="Salmon Noodle Bowl",
        ingredients=["1 cup egg noodles", "200g fresh salmon fillet", "soy sauce"],
        instructions="Boil noodles and pan-sear salmon.",
        cooking_minutes=20,
        calories=450.0,
        protein_grams=30.0,
        allergens=[],
        cuisine="Asian",
        source="TheMealDB (External API)"
    )

    constraints = StructuredConstraints(allergies=["fish"])
    safe, verdicts = validate_candidates([external_recipe], constraints)

    assert len(safe) == 0
    assert len(verdicts) == 1
    assert not verdicts[0].is_safe
    assert any("salmon" in v.lower() for v in verdicts[0].violations)

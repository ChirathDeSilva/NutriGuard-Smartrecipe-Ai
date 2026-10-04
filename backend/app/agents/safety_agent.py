"""
AGENT 3: Safety Agent (NutriGuard Core Food Safety Guardrail)
=============================================================
CRITICAL ARCHITECTURAL RULE:
- ZERO LLM CALLS ALLOWED.
- 100% deterministic Python set logic, substring searching, and numerical threshold checks.
- Validates candidate recipes against user allergies, dietary restrictions, and calorie limits.
"""

from typing import List, Tuple, Set
from backend.app.db.schemas import CandidateRecipe, StructuredConstraints, SafetyVerdict

# Canonical allergen synonyms and ingredient keywords for comprehensive string scanning
COMMON_ALLERGEN_KEYWORDS = {
    "peanuts": {"peanut", "peanuts", "groundnut", "groundnuts", "peanut butter", "peanut oil"},
    "tree nuts": {"cashew", "cashews", "almond", "almonds", "walnut", "walnuts", "pistachio", "pistachios", "hazelnut"},
    "dairy": {"dairy", "cow milk", "whole milk", "skim milk", "butter", "cheese", "yogurt", "ghee", "paneer", "curd", "cream", "whey", "heavy cream"},
    "eggs": {"egg", "eggs", "egg yolk", "egg white", "mayonnaise"},
    "gluten": {"wheat", "gluten", "barley", "rye", "wheat flour", "bread", "atta", "maida", "semolina"},
    "fish": {"fish", "maldive fish", "maldive fish flakes", "tuna", "tuna flakes", "salmon", "anchovy", "fish sauce"},
    "shellfish": {"prawn", "prawns", "shrimp", "shrimps", "crab", "crabs", "lobster", "crayfish", "clam", "oyster"},
    "soy": {"soy", "soya", "soy sauce", "tofu", "edamame", "soybean", "soy milk"},
    "sesame": {"sesame", "tahini", "sesame seeds", "sesame oil"}
}

# Plant-based milks that are completely dairy-free
PLANT_MILK_EXCEPTIONS = {"coconut milk", "almond milk", "soy milk", "oat milk", "rice milk", "cashew milk"}

# Ingredients strictly prohibited for common diet types
DIET_RESTRICTIONS = {
    "vegan": {
        "meat": {"chicken", "beef", "pork", "mutton", "lamb", "meat", "bacon", "turkey"},
        "seafood": {"fish", "prawn", "shrimp", "crab", "maldive fish", "tuna", "salmon", "anchovy", "shellfish"},
        "dairy": {"cow milk", "butter", "cheese", "curd", "ghee", "yogurt", "cream", "whey", "paneer"},
        "eggs": {"egg", "eggs", "mayonnaise"},
        "other": {"honey"}
    },
    "vegetarian": {
        "meat": {"chicken", "beef", "pork", "mutton", "lamb", "meat", "bacon", "turkey"},
        "seafood": {"fish", "prawn", "shrimp", "crab", "maldive fish", "tuna", "salmon", "anchovy", "shellfish"}
    },
    "keto": {
        "high_carb": {"sugar", "rice", "wheat flour", "potatoes", "cassava", "corn"}
    }
}


def _normalize_text(text: str) -> str:
    """Normalize text to lowercase and stripped string."""
    return text.strip().lower()


def _get_allergen_keywords(allergen: str) -> Set[str]:
    """Retrieve keywords and aliases associated with an allergen."""
    norm = _normalize_text(allergen)
    for canonical, keywords in COMMON_ALLERGEN_KEYWORDS.items():
        if norm == canonical or norm in keywords:
            return keywords | {norm}
    return {norm}


def validate_candidates(
    candidates: List[CandidateRecipe],
    constraints: StructuredConstraints
) -> Tuple[List[CandidateRecipe], List[SafetyVerdict]]:
    """
    Deterministically evaluates a list of CandidateRecipe objects against user constraints.

    Returns:
        Tuple of:
          - safe_recipes: List of CandidateRecipe that passed 100% of safety checks
          - verdicts: List of SafetyVerdict recording pass/block audit decisions
    """
    safe_recipes: List[CandidateRecipe] = []
    verdicts: List[SafetyVerdict] = []

    # Normalize user allergies
    user_allergies = {_normalize_text(a) for a in (constraints.allergies or [])}
    user_diet = _normalize_text(constraints.diet_type) if constraints.diet_type else None
    max_calories = constraints.max_calories

    for recipe in candidates:
        violations: List[str] = []

        # ----------------------------------------------------------------------
        # 1. Deterministic Allergen Check: Declared Recipe Allergens
        # ----------------------------------------------------------------------
        recipe_allergens = {_normalize_text(a) for a in (recipe.allergens or [])}
        for u_allergen in user_allergies:
            u_keywords = _get_allergen_keywords(u_allergen)
            # Check if any declared recipe allergen matches user allergen keywords
            if any(ra in u_keywords for ra in recipe_allergens):
                violations.append(f"Contains declared allergen '{u_allergen}'")

        # ----------------------------------------------------------------------
        # 2. Deterministic Allergen Check: Deep Ingredient String Scanning
        # ----------------------------------------------------------------------
        recipe_ingredients_lower = [_normalize_text(i) for i in recipe.ingredients]
        for u_allergen in user_allergies:
            keywords = _get_allergen_keywords(u_allergen)
            for ing in recipe_ingredients_lower:
                for kw in keywords:
                    if kw in ing:
                        msg = f"Ingredient '{ing}' triggers allergen keyword '{kw}' (Allergy: {u_allergen})"
                        if msg not in violations:
                            violations.append(msg)

        # ----------------------------------------------------------------------
        # 3. Deterministic Dietary Lifestyle Check (Vegan, Vegetarian, etc.)
        # ----------------------------------------------------------------------
        if user_diet:
            if user_diet in ["vegan", "vegetarian"]:
                prohibited_categories = DIET_RESTRICTIONS[user_diet]
                for cat_name, bad_items in prohibited_categories.items():
                    for ing in recipe_ingredients_lower:
                        for bad in bad_items:
                            if bad in ing:
                                msg = f"Ingredient '{ing}' violates '{user_diet}' diet restriction ({cat_name}: {bad})"
                                if msg not in violations:
                                    violations.append(msg)

            elif user_diet == "keto":
                # Keto hard limit: carbs > 25g
                if recipe.carbs_grams > 25.0:
                    violations.append(f"Carbohydrates ({recipe.carbs_grams}g) exceed strict keto threshold (25g)")

        # ----------------------------------------------------------------------
        # 4. Deterministic Calorie Ceiling Check
        # ----------------------------------------------------------------------
        if max_calories is not None and max_calories > 0:
            if recipe.calories > max_calories:
                violations.append(f"Calories ({recipe.calories} kcal) exceed requested maximum ({max_calories} kcal)")

        # ----------------------------------------------------------------------
        # 5. Compile Verdict
        # ----------------------------------------------------------------------
        is_safe = len(violations) == 0
        verdict = SafetyVerdict(
            recipe_id=recipe.id,
            is_safe=is_safe,
            violations=violations
        )
        verdicts.append(verdict)

        if is_safe:
            safe_recipes.append(recipe)

    return safe_recipes, verdicts

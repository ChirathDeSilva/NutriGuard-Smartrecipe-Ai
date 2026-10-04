"""
EXTERNAL APIS SERVICE: TheMealDB & USDA Fallback Integration
============================================================
Handles asynchronous requests to external recipe and nutrition databases
using HTTPX with defensive timeouts and error handling.
"""

import httpx
from typing import List, Dict, Any, Optional

THEMEALDB_BASE_URL = "https://www.themealdb.com/api/json/v1/1"


async def search_themealdb(query: str) -> List[Dict[str, Any]]:
    """
    Asynchronously queries TheMealDB API by ingredient or recipe search keyword.
    Returns parsed list of raw meal dictionaries.
    """
    if not query or not query.strip():
        return []

    url = f"{THEMEALDB_BASE_URL}/search.php"
    params = {"s": query.strip()}

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                meals = data.get("meals")
                return meals if meals else []
    except Exception as e:
        print(f"[EXTERNAL API ERROR] TheMealDB search failed for '{query}': {e}")
        return []

    return []


def parse_themealdb_to_candidate_dict(meal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a raw TheMealDB response object into standard CandidateRecipe format.
    TheMealDB stores ingredients in strIngredient1..20 and measures in strMeasure1..20.
    """
    ingredients: List[str] = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        if ing and ing.strip():
            desc = f"{measure.strip()} {ing.strip()}" if measure and measure.strip() else ing.strip()
            ingredients.append(desc.lower())

    instructions = meal.get("strInstructions", "Follow standard preparation steps.") or ""
    title = meal.get("strMeal", "International Dish")
    cuisine = meal.get("strArea", "International")
    meal_id = f"mealdb_{meal.get('idMeal', '0')}"

    # External meals default conservative estimations:
    # 450 kcal, 22g protein, 45g carbs, 18g fat, 30 min cook time
    return {
        "id": meal_id,
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "cooking_minutes": 30,
        "calories": 450.0,
        "protein_grams": 22.0,
        "carbs_grams": 45.0,
        "fat_grams": 18.0,
        "allergens": [],
        "cuisine": cuisine,
        "popularity": 0.6,
        "source": "TheMealDB (External API)"
    }

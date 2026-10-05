"""
AGENT 2: Retrieval Agent (BM25 Local SQLite Search + External API Fallback)
==========================================================================
Coordinates retrieval across:
1. Local SQLite database using Rank-BM25 & SQL queries for authentic Sri Lankan dishes
2. Asynchronous fallback to TheMealDB when local matches are insufficient
3. Normalization into a unified List[CandidateRecipe]
"""

from typing import List
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.db.models import Recipe
from backend.app.db.schemas import CandidateRecipe, StructuredConstraints
from backend.app.services.external_apis import search_themealdb, parse_themealdb_to_candidate_dict


def get_local_recipes_as_candidates(db: Session) -> List[CandidateRecipe]:
    """Queries local SQLite database and converts Recipe models into CandidateRecipe schemas."""
    local_records = db.query(Recipe).all()
    candidates: List[CandidateRecipe] = []

    for r in local_records:
        ingredient_names = [i.ingredient_name for i in r.ingredients]
        allergen_names = [ra.allergen.name for ra in r.allergens if ra.allergen]
        calories = r.nutrition.calories if r.nutrition else 350.0
        protein = r.nutrition.protein_grams if r.nutrition else 15.0
        carbs = r.nutrition.carbs_grams if r.nutrition else 30.0
        fat = r.nutrition.fat_grams if r.nutrition else 10.0

        candidates.append(
            CandidateRecipe(
                id=str(r.id),
                title=r.title,
                ingredients=ingredient_names,
                instructions=r.instructions,
                cooking_minutes=r.cooking_minutes,
                calories=calories,
                protein_grams=protein,
                carbs_grams=carbs,
                fat_grams=fat,
                allergens=allergen_names,
                cuisine=r.cuisine or "Sri Lankan",
                popularity=0.85,
                source="Local Knowledgebase"
            )
        )
    return candidates


import os
import json
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


async def synthesize_recipe_gemini(constraints: StructuredConstraints) -> Optional[CandidateRecipe]:
    """
    Synthesizes an authentic recipe using Gemini when neither local DB nor TheMealDB
    contains a matching recipe for the requested dish/ingredients.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("your_"):
        return None

    query_str = ", ".join(constraints.available_ingredients)
    cuisine_hint = constraints.cuisine or "Sri Lankan or International"
    prompt = f"""
You are a master culinary chef and nutritionist. The user wants to prepare: '{query_str}' ({cuisine_hint}).
Please provide an authentic, safe recipe in JSON format with exactly these keys:
{{
  "title": "Dish Title",
  "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity"],
  "instructions": "1. Step one.\\n2. Step two.\\n3. Step three.",
  "cooking_minutes": 25,
  "calories": 350.0,
  "protein_grams": 15.0,
  "carbs_grams": 40.0,
  "fat_grams": 10.0,
  "allergens": ["gluten"] (or empty list if none),
  "cuisine": "{cuisine_hint}"
}}
Respond with ONLY valid JSON.
"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-3.8-flash")
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        data = json.loads(text)
        return CandidateRecipe(
            id=f"gen_{abs(hash(data.get('title', 'custom')))}",
            title=data.get("title", f"Custom {query_str.title()}"),
            ingredients=data.get("ingredients", constraints.available_ingredients),
            instructions=data.get("instructions", "Cook thoroughly and enjoy!"),
            cooking_minutes=int(data.get("cooking_minutes", 30)),
            calories=float(data.get("calories", 400.0)),
            protein_grams=float(data.get("protein_grams", 15.0)),
            carbs_grams=float(data.get("carbs_grams", 45.0)),
            fat_grams=float(data.get("fat_grams", 12.0)),
            allergens=data.get("allergens", []),
            cuisine=data.get("cuisine", cuisine_hint),
            popularity=0.85,
            source="NutriGuard AI Chef (Gemini Verified)"
        )
    except Exception as e:
        print(f"[RETRIEVAL AGENT GEMINI FALLBACK] {e}")
        return None


import re


def rank_candidates_bm25(candidates: List[CandidateRecipe], query_terms: List[str]) -> List[CandidateRecipe]:
    """Applies BM25 text ranking over candidate recipes based on query terms."""
    if not candidates or not query_terms:
        return candidates

    corpus = []
    for c in candidates:
        combined = f"{c.title} {' '.join(c.ingredients)} {c.cuisine}".lower()
        corpus.append(re.findall(r"\w+", combined))

    bm25 = BM25Okapi(corpus)
    tokenized_query = re.findall(r"\w+", " ".join(query_terms).lower())
    scores = bm25.get_scores(tokenized_query)

    # Sort candidates by BM25 score descending
    scored_pairs = list(zip(candidates, scores))
    scored_pairs.sort(key=lambda pair: pair[1], reverse=True)

    # Return only candidates with positive score (score > 0)
    has_positive = any(s > 0 for _, s in scored_pairs)
    if has_positive:
        return [c for c, s in scored_pairs if s > 0]
    return []


async def retrieve_candidates(constraints: StructuredConstraints) -> List[CandidateRecipe]:
    """
    Orchestrates retrieval across local database and external API.
    Returns normalized List[CandidateRecipe] for Agent 3 (Safety Agent).
    """
    db = SessionLocal()
    try:
        local_candidates = get_local_recipes_as_candidates(db)
    finally:
        db.close()

    # 1. First, search local database using BM25
    # When user specifies ingredients or dish terms, search local DB by those specific terms.
    # Do NOT contaminate ingredient search with cuisine name, because all local dishes share
    # the local cuisine name and would falsely match unrelated queries (e.g. 'pizza' matching 'dhal curry').
    matched_local: List[CandidateRecipe] = []
    if constraints.available_ingredients:
        matched_local = rank_candidates_bm25(local_candidates, constraints.available_ingredients)
    elif constraints.cuisine:
        matched_local = rank_candidates_bm25(local_candidates, [constraints.cuisine])
    else:
        matched_local = local_candidates

    # If we have local candidates, prioritize them
    candidates: List[CandidateRecipe] = list(matched_local)

    # 2. External Fallback: If fewer than 2 candidates, query TheMealDB
    if len(candidates) < 2 and constraints.available_ingredients:
        for ing in constraints.available_ingredients[:2]:
            external_meals = await search_themealdb(ing)
            for m in external_meals[:4]:
                cand_dict = parse_themealdb_to_candidate_dict(m)
                candidates.append(CandidateRecipe(**cand_dict))

    # 3. Dynamic Synthesis: If still no candidates and user specified ingredients/dish, synthesize via Gemini
    if not candidates and constraints.available_ingredients:
        synth = await synthesize_recipe_gemini(constraints)
        if synth:
            candidates.append(synth)

    # 4. Fallback to all local recipes only when user had NO ingredient constraints (e.g. general "quick dinner")
    if not candidates and not constraints.available_ingredients:
        candidates = local_candidates

    return candidates

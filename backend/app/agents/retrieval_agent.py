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


def rank_candidates_bm25(candidates: List[CandidateRecipe], query_terms: List[str]) -> List[CandidateRecipe]:
    """Applies BM25 text ranking over candidate recipes based on query terms."""
    if not candidates or not query_terms:
        return candidates

    corpus = []
    for c in candidates:
        text = f"{c.title} {' '.join(c.ingredients)} {c.cuisine}".lower().split()
        corpus.append(text)

    bm25 = BM25Okapi(corpus)
    tokenized_query = [t.lower() for t in query_terms]
    scores = bm25.get_scores(tokenized_query)

    # Sort candidates by BM25 score descending
    scored_pairs = list(zip(candidates, scores))
    scored_pairs.sort(key=lambda pair: pair[1], reverse=True)

    # Filter out candidates with zero score if we have matches with >0 score
    has_positive = any(s > 0 for _, s in scored_pairs)
    if has_positive:
        return [c for c, s in scored_pairs if s > 0]
    return candidates


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

    # Search query terms: ingredients + cuisine preference
    query_terms = list(constraints.available_ingredients)
    if constraints.cuisine:
        query_terms.append(constraints.cuisine)

    # 1. First, search local database using BM25
    matched_local: List[CandidateRecipe] = []
    if query_terms:
        matched_local = rank_candidates_bm25(local_candidates, query_terms)
    else:
        matched_local = local_candidates

    # If we have local candidates, prioritize them
    candidates: List[CandidateRecipe] = list(matched_local)

    # 2. External Fallback: If fewer than 2 candidates, query TheMealDB
    if len(candidates) < 2 and constraints.available_ingredients:
        for ing in constraints.available_ingredients[:2]:
            external_meals = await search_themealdb(ing)
            for m in external_meals[:2]:
                cand_dict = parse_themealdb_to_candidate_dict(m)
                candidates.append(CandidateRecipe(**cand_dict))

    # Fallback to all local recipes if nothing was matched
    if not candidates:
        candidates = local_candidates

    return candidates

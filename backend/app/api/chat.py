"""
CHAT API ROUTE: 5-Agent Sequential Pipeline Orchestrator
========================================================
Exposes POST /api/chat. Coordinates the 5 sequential agents:
1. Agent 1: spaCy NLP Query Parsing -> StructuredConstraints
2. Agent 2: BM25 Local + TheMealDB Retrieval -> CandidateRecipes
3. Agent 3: Deterministic Zero-LLM Safety Verification -> Safe Candidates
   * If zero candidates pass safety checks, returns HTTP 400 with exact safety audit violations
4. Agent 4: Linear Weighted Multi-Factor Ranking -> Top RankedRecipe
5. Agent 5: Grounded Response Synthesis -> FinalAgentResponse
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import AuditLog
from backend.app.db.schemas import UserQueryRequest, FinalAgentResponse
from backend.app.core.security import sanitize_input
from backend.app.agents import query_agent, retrieval_agent, safety_agent, ranking_agent, response_agent

router = APIRouter(tags=["Chat & Recipe Pipeline"])


@router.post("/chat", response_model=FinalAgentResponse)
async def chat_pipeline(request: UserQueryRequest, db: Session = Depends(get_db)):
    """
    Executes the complete 5-agent NutriGuard pipeline sequentially.
    """
    # 0. Input Sanitization
    clean_prompt = sanitize_input(request.prompt)
    if not clean_prompt:
        raise HTTPException(status_code=400, detail="User prompt cannot be empty or solely invalid tokens.")
    request.prompt = clean_prompt

    # 1. AGENT 1: Query Agent (spaCy NLP & Constraint Extraction)
    constraints = query_agent.parse_query(request)

    # --------------------------------------------------------------------------
    # INTENT HANDLING: Greetings, FAQs, and Unrelated Topics
    # --------------------------------------------------------------------------
    if constraints.intent == "greeting":
        greeting_text = (
            "👋 **Hello! Welcome to NutriGuard AI.**\n\n"
            "I am your personal culinary food safety and recipe recommendation assistant. "
            "Tell me what ingredients you have in your kitchen (e.g., *chicken, red lentils, coconut milk, shallots*), "
            "or what kind of dish you would like to prepare. I will search our recipe database, strictly verify "
            "all food allergens, and recommend the healthiest, safest recipe for you!"
        )
        return FinalAgentResponse(
            response_type="conversational",
            message=greeting_text,
            recipe_title=None,
            score=0.0
        )

    if constraints.intent == "unrelated":
        unrelated_text = (
            "⚠️ **Out of Scope Question:**\n\n"
            "I specialize exclusively in **food, recipes, cooking instructions, dietary lifestyles, and food allergy safety**.\n\n"
            "I cannot assist with unrelated topics like technology, politics, general chat, or finance. "
            "Please ask me about a recipe or tell me what ingredients you have to cook with!"
        )
        return FinalAgentResponse(
            response_type="conversational",
            message=unrelated_text,
            recipe_title=None,
            score=0.0
        )

    # 2. AGENT 2: Retrieval Agent (BM25 SQLite + External API Fallback)
    candidates = await retrieval_agent.retrieve_candidates(constraints)
    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="No matching recipes found in local database or external sources."
        )

    # 3. AGENT 3: Safety Agent (100% Deterministic Python Logic - ZERO LLM)
    safe_candidates, verdicts = safety_agent.validate_candidates(candidates, constraints)

    # If NO candidates passed safety checks, enforce strict safety guardrail
    if not safe_candidates:
        # Collect all explicit safety violations to audit log
        all_violations = []
        for v in verdicts:
            all_violations.extend(v.violations)

        # Log safety block event in SQLite AuditLog table
        audit_entry = AuditLog(
            user_id=request.user_id,
            event_type="ALLERGEN_SAFETY_BLOCKED",
            resource_type="recipe_batch",
            status="BLOCKED",
            extra_metadata=f"Blocked {len(candidates)} candidates. Violations: {'; '.join(all_violations)}"
        )
        db.add(audit_entry)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail={
                "message": "All retrieved recipes were blocked by NutriGuard Food Safety Guardrails.",
                "reason": "Safety violations detected for your requested dietary or allergen constraints.",
                "violations": list(set(all_violations))
            }
        )

    # 4. AGENT 4: Ranking Agent (Linear Weighted Multi-Factor Scoring Formula)
    best_recipe = ranking_agent.rank(safe_candidates, constraints)
    if not best_recipe:
        raise HTTPException(status_code=500, detail="Failed to rank safe recipe candidates.")

    # 5. AGENT 5: Response Agent (Grounded Gemini LLM Explanation)
    final_response = await response_agent.generate_response(best_recipe)

    # Log successful recommendation event
    audit_success = AuditLog(
        user_id=request.user_id,
        event_type="RECIPE_RECOMMENDED",
        resource_type="recipe",
        resource_id=best_recipe.recipe.id,
        status="SUCCESS",
        extra_metadata=f"Title: {best_recipe.recipe.title}, Score: {best_recipe.final_score}"
    )
    db.add(audit_success)
    db.commit()

    return final_response

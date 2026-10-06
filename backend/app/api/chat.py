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

import re

router = APIRouter(tags=["Chat & Recipe Pipeline"])

KNOWN_DISH_INFO = {
    # --- International Classics ---
    "pizza": (
        "**Pizza** is a beloved Italian culinary classic featuring a leavened dough crust topped with rich tomato sauce, "
        "melted mozzarella or plant-based cheese, and savory toppings like basil, mushrooms, or roasted meats. "
        "At NutriGuard, we help you prepare light, balanced crusts with fresh herbs and allergen-safe toppings."
    ),
    "pasta": (
        "**Pasta** is a versatile Italian staple made from durum wheat semolina or gluten-free grains, boiled al dente "
        "and paired with vibrant marinara, basil pesto, or light olive oil emulsions. It offers energizing complex carbohydrates."
    ),
    "burger": (
        "**Burger** is an iconic dish featuring a seasoned patty—made from lean poultry, beef, or nutrient-dense plant proteins "
        "like black beans or lentils—served inside a toasted bun with crisp lettuce, ripe tomatoes, and gourmet relish."
    ),
    "sushi": (
        "**Sushi** is a refined Japanese culinary tradition pairing seasoned vinegared rice with fresh fish, seafood, avocado, "
        "and crisp nori seaweed. It is celebrated worldwide for its clean flavors, high protein, and omega-3 fatty acids."
    ),
    "biryani": (
        "**Biryani** is a majestic South Asian rice dish featuring aged long-grain basmati rice layered with tender spiced meats "
        "or vegetables, saffron, caramelized shallots, and whole spices like cardamom, cloves, and star anise."
    ),
    "tacos": (
        "**Tacos** are a vibrant Mexican culinary staple featuring soft corn or flour tortillas folded around spiced proteins, "
        "fresh salsa, crunchy cabbage, and zesty lime juice, providing a balanced blend of fiber, protein, and bold flavors."
    ),
    "noodles": (
        "**Noodles** are a beloved global comfort food, from Asian stir-fried wok noodles to rich brothy ramen, "
        "easily customized with colorful vegetables, lean proteins, and low-sodium savory sauces."
    ),
    "salad": (
        "**Salad** is a nutrient-dense dish composed of crisp leafy greens, crunchy vegetables, seeds, nuts, and healthy vinaigrettes, "
        "delivering vital antioxidants, dietary fiber, and micronutrients."
    ),
    "soup": (
        "**Soup** is a deeply nourishing liquid dish created by simmering wholesome vegetables, legumes, or tender meats "
        "with fragrant herbs and aromatics, perfect for gentle digestion and optimal hydration."
    ),

    # --- Sri Lankan Heritage Dishes ---
    "roti": (
        "**Roti** (such as Sri Lankan Pol Roti) is a rustic traditional flatbread made with wheat flour, "
        "fresh grated coconut, diced shallots, and green chilies, toasted to golden perfection on a dry griddle."
    ),
    "pol roti": (
        "**Pol Roti** is a quintessential Sri Lankan flatbread crafted from fresh grated coconut, wheat flour, "
        "green chilies, shallots, and salt. Crispy on the crust and soft inside, it pairs perfectly with spicy Pol Sambol or Dhal."
    ),
    "hoppers": (
        "**Hoppers** (Appa) are iconic bowl-shaped Sri Lankan pancakes made from fermented rice flour batter and coconut milk, "
        "distinguished by a crisp golden lace edge and a soft, pillowy, steaming center."
    ),
    "string hoppers": (
        "**String Hoppers** (Idiyappam) are delicate steamed rice noodle nests, traditionally served for breakfast or dinner "
        "with turmeric coconut milk gravy (Kiri Hodi), Pol Sambol, or meat curry."
    ),
    "pol sambol": (
        "**Pol Sambol** is a vibrant, spicy, and tangy Sri Lankan coconut relish prepared by pounding freshly scraped coconut "
        "with whole red chili, shallots, lime juice, and salt (traditionally enhanced with umami Maldive fish flakes)."
    ),
    "dhal": (
        "**Dhal Curry** (Parippu) is a comforting, golden red lentil curry gently simmered in creamy coconut milk, turmeric, "
        "curry leaves, tempered mustard seeds, and garlic. It forms the nutritional backbone of everyday Sri Lankan dining."
    ),
    "dhal curry": (
        "**Dhal Curry** (Parippu) is a comforting, golden red lentil curry gently simmered in creamy coconut milk, turmeric, "
        "curry leaves, tempered mustard seeds, and garlic. It is high in plant protein and dietary fiber."
    ),
    "kottu": (
        "**Kottu Roti** is Sri Lanka's ultimate street food sensation: chopped godamba flatbread stir-fried on an iron griddle "
        "with vegetables, eggs, spices, and rich curry gravy with an energetic culinary rhythm."
    ),
    "kottu roti": (
        "**Kottu Roti** is Sri Lanka's ultimate street food sensation: chopped godamba flatbread stir-fried on an iron griddle "
        "with vegetables, eggs, spices, and rich curry gravy with an energetic culinary rhythm."
    ),
    "chicken curry": (
        "**Sri Lankan Chicken Curry** (Kukul Mas Curry) is deeply aromatic and robust, cooked with roasted Ceylon curry powder, "
        "pandan leaves, lemongrass, ginger, garlic, and rich coconut milk."
    ),
    "ambul thiyal": (
        "**Fish Ambul Thiyal** is an iconic Southern Sri Lankan dry fish curry prepared with Goraka paste, crushed black pepper, "
        "and firm tuna, slow-simmered in an earthen clay pot until deep, sour, and intensely flavorful."
    ),
    "kaju curry": (
        "**Cashew Nut Curry** (Kaju Curry) is a luxurious, creamy celebratory curry of tender whole raw cashews and sweet green peas "
        "simmered in rich coconut milk and aromatic Ceylon spices."
    ),
    "kiribath": (
        "**Kiribath** (Milk Rice) is an auspicious festive staple made by cooking white rice in thick salted coconut milk until creamy, "
        "cut into traditional diamond cakes and paired with spicy Lunu Miris or Seeni Sambol."
    ),
    "polos": (
        "**Polos Curry** is a slow-cooked young baby jackfruit curry celebrated for its meaty texture, cooked with dark roasted Ceylon spices, "
        "Goraka, and coconut milk, offering exceptional dietary fiber."
    ),
    "wambatu moju": (
        "**Wambatu Moju** is a treasured sweet, sour, and spicy eggplant pickle made from deep-fried brinjal slivers tossed with "
        "mustard paste, shallots, green chilies, vinegar, and coconut sugar."
    ),
    "gotu kola": (
        "**Gotu Kola Sambol** is a rejuvenating herbal salad made from finely shredded Centella asiatica leaves tossed with "
        "fresh grated coconut, shallots, lime, and black pepper, prized for its memory and cognitive benefits."
    )
}


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
            "**Welcome to NutriGuard AI**\n\n"
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
            "**Out of Scope Question:**\n\n"
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

    if constraints.intent == "food_question":
        # Extract dish name from questions like 'what is roti' or 'tell me about hoppers'
        clean_food = re.sub(r"^(?:what\s+is|what\s+are|tell\s+me\s+about|explain|describe)\s+", "", request.prompt.strip(), flags=re.IGNORECASE).rstrip("?.").strip()
        clean_lower = clean_food.lower()

        dish_desc = None
        # Sort keys by length descending so "kottu roti" matches before "roti"
        for key in sorted(KNOWN_DISH_INFO.keys(), key=len, reverse=True):
            if key in clean_lower:
                dish_desc = KNOWN_DISH_INFO[key]
                break

        if not dish_desc:
            dish_desc = (
                f"**{clean_food.title()}** is a wonderful culinary dish. In NutriGuard AI, we help you prepare balanced, "
                f"allergy-safe versions tailored to your nutritional preferences and available kitchen ingredients."
            )

        answer = (
            f"**Culinary Guide: {clean_food.title() if clean_food else 'Dish Information'}**\n\n"
            f"{dish_desc}\n\n"
            f"*Would you like a healthy, allergy-safe recipe to make this at home? Tell me your preferred ingredients or dietary limits!*"
        )
        return FinalAgentResponse(
            response_type="conversational",
            message=answer,
            recipe_title=None,
            score=0.0
        )

    # 2. AGENT 2: Retrieval Agent (BM25 SQLite + External API Fallback)
    candidates = await retrieval_agent.retrieve_candidates(constraints)
    if not candidates:
        candidates = retrieval_agent.get_local_recipes_as_candidates(db)

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

"""
AGENT 1: Query Agent (spaCy NLP Entity Extraction & Constraint Parsing)
======================================================================
Extracts structured constraints from conversational user prompts:
- Ingredients extraction using spaCy noun chunks & culinary token filtering
- Cooking time limits using regex patterns (e.g., 'under 30 mins')
- Calorie constraints using regex patterns (e.g., 'under 500 calories')
- Allergy and dietary lifestyle keyword detection
- Returns validated StructuredConstraints Pydantic schema
"""

import re
import spacy
from typing import List, Optional, Dict, Any
from backend.app.db.schemas import UserQueryRequest, StructuredConstraints

# Load spaCy NLP pipeline
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # Fallback to blank model if not yet downloaded
    nlp = spacy.blank("en")

# Known culinary allergens to spot in natural language
KNOWN_ALLERGEN_TERMS = {
    "peanuts": ["peanut", "peanuts", "groundnut"],
    "dairy": ["dairy", "milk", "cheese", "butter", "lactose"],
    "gluten": ["gluten", "wheat", "flour"],
    "fish": ["fish", "seafood", "maldive fish", "tuna"],
    "shellfish": ["shellfish", "prawn", "prawns", "shrimp", "crab"],
    "eggs": ["egg", "eggs"],
    "soy": ["soy", "soya", "tofu"],
    "tree nuts": ["cashew", "cashews", "almond", "almonds", "walnut"]
}

# Known diet types to identify from prompt
KNOWN_DIET_TERMS = {
    "vegan": ["vegan", "plant-based"],
    "vegetarian": ["vegetarian", "veg"],
    "keto": ["keto", "ketogenic", "low carb"]
}

# Conversational Greetings & Chit-chat tokens
GREETING_PATTERNS = [
    r"^(?:hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening|greetings|hola)\b",
    r"^(?:howdy|sup|what'?s\s+up)\b",
    r"^(?:thank\s+you|thanks|thx)\b",
    r"^(?:who\s+are\s+you|what\s+can\s+you\s+do|help|what\s+is\s+nutriguard)\b"
]

# Unrelated topics (tech, coding, politics, weather, finance, gaming, general non-food)
UNRELATED_PATTERNS = [
    r"\b(?:weather|forecast|rain|temperature|climate)\b",
    r"\b(?:stock|stocks|crypto|bitcoin|trading|forex|invest|investment|finance|bank|money)\b",
    r"\b(?:code|coding|python|java|javascript|c\+\+|programming|developer|software|bug|sql|html|css|react)\b",
    r"\b(?:movie|movies|film|song|songs|music|actor|actress|sports|football|cricket|soccer|basketball|game|gaming|nba|fifa)\b",
    r"\b(?:politics|president|election|minister|parliament|government|war|military|army)\b",
    r"\b(?:car|cars|vehicle|repair|flight|flights|hotel|hotels|airline|airport)\b",
    r"\b(?:math|calculus|algebra|physics|chemistry|homework|essay|history|geography|capital\s+of)\b",
    r"\b(?:phone|computer|laptop|iphone|android|windows|hardware|wifi)\b",
    r"\b(?:joke|riddle|story|poem|poetry)\b"
]

# Culinary & recipe keywords
CULINARY_KEYWORDS = {
    "cook", "cooking", "recipe", "recipes", "curry", "dish", "dishes", "make", "eat", "eating",
    "dinner", "lunch", "breakfast", "snack", "meal", "meals", "ingredient", "ingredients",
    "spices", "chicken", "lentils", "dhal", "rice", "sambol", "fish", "soup", "salad", "food",
    "calories", "bake", "baking", "fry", "frying", "boil", "boiling", "roti", "hoppers", "kottu",
    "flour", "coconut", "vegetable", "vegetables", "meat", "beef", "pork", "shrimp", "seafood",
    "vegan", "vegetarian", "nutrition", "diet"
}

# Common culinary food/ingredient items to ensure reliable entity extraction
# even when spaCy POS tagging misidentifies tokens (e.g. 'chicken' or 'fish' as verbs)
COMMON_FOOD_TERMS = [
    "chicken", "beef", "pork", "lamb", "mutton", "fish", "prawn", "prawns", "shrimp", "shrimps",
    "crab", "crabs", "egg", "eggs", "lentil", "lentils", "dhal", "dal", "rice", "cashew", "cashews",
    "coconut", "coconut milk", "jackfruit", "polos", "eggplant", "brinjal", "potato", "potatoes",
    "tomato", "tomatoes", "onion", "shallot", "shallots", "garlic", "ginger", "lemongrass", "chili",
    "chilies", "pepper", "flour", "cheese", "pasta", "pizza", "noodles", "mushroom", "mushrooms",
    "spinach", "tofu", "paneer", "salmon", "tuna", "turkey", "duck", "bacon", "sausage", "beans",
    "peas", "chickpeas", "avocado", "broccoli", "carrot", "carrots", "cucumber", "cabbage",
    "curry leaves", "pandan", "coriander", "cumin", "fenugreek", "cinnamon", "cardamom", "cloves",
    "mustard", "roti", "pol roti", "hoppers", "string hoppers", "pol sambol", "biryani", "kiribath",
    "ambul thiyal", "kottu", "vada", "vadai"
]

# Stopwords/filler words that should not be parsed as ingredients
IGNORE_WORDS = {
    "recipe", "recipes", "food", "dinner", "lunch", "breakfast", "dish",
    "quick", "fast", "healthy", "meal", "something", "want", "have", "cook",
    "make", "give", "minutes", "mins", "calories", "kcal", "time", "sri lankan",
    "i", "me", "my", "we", "under", "about", "around", "less", "more", "need",
    "hi", "hello", "hey", "please", "can", "you", "tell", "show",
    "it", "this", "that", "them", "these", "those", "how", "what", "which",
    "where", "who", "whom", "why", "way", "to", "do", "does", "did", "is",
    "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "with", "without", "for", "of", "in", "on", "at", "by", "from", "the",
    "a", "an", "step", "steps", "instructions", "prepare"
}


def resolve_context_dish(conversation_history: List[Dict[str, Any]]) -> Optional[str]:
    """
    Extracts the most recently discussed culinary dish from conversation history.
    Searches both recent assistant culinary guides/recommendations and user food queries.
    """
    if not conversation_history:
        return None

    for msg in reversed(conversation_history[-5:]):
        content = str(msg.get("content", ""))

        # 1. Match from "Culinary Guide: <Dish>" header
        guide_match = re.search(r"Culinary Guide:\s*([^\n\r*:]+)", content, re.IGNORECASE)
        if guide_match:
            dish = guide_match.group(1).strip()
            if dish and dish.lower() not in {"recipe information", "dish information"}:
                return dish

        # 2. Match from "**<Dish>** is a..." pattern
        bold_match = re.search(r"\*\*([^\n\r*]+)\*\*\s+(?:is|are)\b", content, re.IGNORECASE)
        if bold_match:
            dish = bold_match.group(1).strip()
            if 0 < len(dish.split()) <= 4 and dish.lower() not in {"this dish", "recipe information", "nutriguard ai"}:
                return dish

        # 3. Match from user query: "what is <dish>" or "tell me about <dish>"
        user_food_match = re.search(r"^(?:what\s+is|what\s+are|tell\s+me\s+about|explain)\s+([^\n\r?.]+)", content, re.IGNORECASE)
        if user_food_match:
            dish = user_food_match.group(1).strip()
            if dish:
                return dish

        # 4. Match from recipe recommendation: "Recommended Recipe: <Title>"
        recipe_title_match = re.search(r"(?:Recommended Recipe:|Title:)\s*([^\n\r]+)", content, re.IGNORECASE)
        if recipe_title_match:
            dish = recipe_title_match.group(1).strip()
            if dish:
                return dish

    return None


def parse_query(request: UserQueryRequest) -> StructuredConstraints:
    """
    Parses a UserQueryRequest into a StructuredConstraints object using NLP and regex.
    Combines user prompt text with sidebar widget selections and multi-turn context.
    """
    prompt = request.prompt.strip()
    prompt_lower = prompt.lower()

    # Multi-turn Context Resolution: Check if prompt refers to a previously discussed dish
    has_pronoun_reference = bool(re.search(r"\b(?:it|this|that|them|same|the dish)\b", prompt_lower))
    is_asking_how = bool(re.search(r"\b(?:how\s+to\s+make|how\s+do\s+you\s+make|how\s+can\s+i\s+make|how\s+do\s+i\s+make|how\s+to\s+cook|how\s+to\s+create|how\s+to\s+prepare|recipe\s+for|make\s+it|cook\s+it|create\s+it|prepare\s+it|bake\s+it)\b", prompt_lower))

    context_dish: Optional[str] = None
    if (has_pronoun_reference or is_asking_how) and request.conversation_history:
        context_dish = resolve_context_dish(request.conversation_history)
        if context_dish:
            # Substitute pronoun with actual dish name in prompt
            prompt_lower = re.sub(r"\b(?:it|this|that|them|the dish)\b", context_dish.lower(), prompt_lower)
            if context_dish.lower() not in prompt_lower:
                prompt_lower = f"{prompt_lower} {context_dish.lower()}"

    # --------------------------------------------------------------------------
    # 1. Regex Extraction: Cooking Time Limit
    # --------------------------------------------------------------------------
    max_time: Optional[int] = request.max_cooking_time
    if max_time is None:
        time_match = re.search(r"(\d+)\s*(?:mins?|minutes?)", prompt_lower)
        if time_match:
            try:
                max_time = int(time_match.group(1))
            except ValueError:
                pass

    # --------------------------------------------------------------------------
    # 2. Regex Extraction: Calorie Ceiling
    # --------------------------------------------------------------------------
    max_cal: Optional[float] = request.calorie_limit
    if max_cal is None:
        cal_match = re.search(r"(\d+)\s*(?:calories?|kcal)", prompt_lower)
        if cal_match:
            try:
                max_cal = float(cal_match.group(1))
            except ValueError:
                pass

    # --------------------------------------------------------------------------
    # 3. Detect Allergies from Natural Language + UI Form
    # --------------------------------------------------------------------------
    allergies_set = set(request.allergies)

    # Detect patterns like "allergic to fish" or "no peanuts"
    for canonical, terms in KNOWN_ALLERGEN_TERMS.items():
        for term in terms:
            if re.search(rf"\b(?:allergic to|no|without|avoid)\s+{term}\b", prompt_lower) or term in prompt_lower:
                if f"allergic to {term}" in prompt_lower or f"no {term}" in prompt_lower or f"without {term}" in prompt_lower:
                    allergies_set.add(canonical)

    # --------------------------------------------------------------------------
    # 4. Detect Dietary Lifestyle
    # --------------------------------------------------------------------------
    diet_type: Optional[str] = None
    if request.dietary_preferences:
        diet_type = request.dietary_preferences[0]
    else:
        for canonical, terms in KNOWN_DIET_TERMS.items():
            for term in terms:
                if re.search(rf"\b{term}\b", prompt_lower):
                    diet_type = canonical
                    break
            if diet_type:
                break

    # Cuisine preference
    cuisine = request.cuisine_preference or ("Sri Lankan" if "sri lankan" in prompt_lower else None)

    # --------------------------------------------------------------------------
    # 4. Intent Classification: greeting, food_question, unrelated, or recipe_search
    # --------------------------------------------------------------------------
    is_greeting = any(re.search(pat, prompt_lower) for pat in GREETING_PATTERNS)
    is_unrelated = any(re.search(pat, prompt_lower) for pat in UNRELATED_PATTERNS)
    prompt_tokens = set(re.findall(r"\b[a-z]+\b", prompt_lower))
    has_culinary = bool(prompt_tokens.intersection(CULINARY_KEYWORDS))

    # Detect conversational food questions (e.g. "what is roti", "tell me about hoppers", "what is pol sambol")
    is_food_question = bool(re.search(r"^(?:what\s+is|what\s+are|tell\s+me\s+about|explain|describe)\s+([a-zA-Z\s]+)", prompt_lower))

    # Priority 1: Unrelated questions (weather, python, stocks, cricket, etc.)
    if is_unrelated and not has_culinary:
        return StructuredConstraints(
            intent="unrelated",
            available_ingredients=[],
            allergies=list(allergies_set),
            diet_type=diet_type,
            max_time_minutes=max_time,
            max_calories=max_cal,
            cuisine=cuisine,
            servings=2
        )

    # Priority 2: Casual greetings and bot capability inquiries
    if is_greeting and not has_culinary:
        return StructuredConstraints(
            intent="greeting",
            available_ingredients=[],
            allergies=list(allergies_set),
            diet_type=diet_type,
            max_time_minutes=max_time,
            max_calories=max_cal,
            cuisine=cuisine,
            servings=2
        )

    # Priority 3: Food knowledge questions (e.g., "what is roti", "tell me about hoppers")
    if is_food_question and not is_unrelated:
        # If user explicitly asks to cook/make a recipe, let it proceed to recipe search
        if not any(w in prompt_lower for w in ["recipe for", "make for me", "give me a recipe", "how to cook"]):
            return StructuredConstraints(
                intent="food_question",
                available_ingredients=[],
                allergies=list(allergies_set),
                diet_type=diet_type,
                max_time_minutes=max_time,
                max_calories=max_cal,
                cuisine=cuisine,
                servings=2
            )

    # --------------------------------------------------------------------------
    # 5. Extract Ingredients via spaCy Noun Chunks
    # --------------------------------------------------------------------------
    available_ingredients: List[str] = []
    doc = nlp(prompt_lower)

    for chunk in doc.noun_chunks:
        chunk_clean = chunk.text.lower().strip()
        # Remove common determiners and leading words
        chunk_clean = re.sub(r"^(?:a|an|the|some|any|my)\s+", "", chunk_clean)

        # Check if words are meaningful ingredients
        words = chunk_clean.split()
        filtered = [w for w in words if w not in IGNORE_WORDS and not w.isdigit()]
        if filtered:
            ingredient_candidate = " ".join(filtered)
            # Avoid re-adding allergens or diets as available ingredients
            if ingredient_candidate not in allergies_set and ingredient_candidate not in KNOWN_DIET_TERMS:
                if ingredient_candidate not in available_ingredients:
                    available_ingredients.append(ingredient_candidate)

    # Supplemental check for known culinary food terms to catch tokens
    # that spaCy POS tagged as verbs or aux (e.g. 'chicken' in 'i have chicken coconut milk')
    for term in sorted(COMMON_FOOD_TERMS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(term) + r"\b", prompt_lower):
            if term not in allergies_set and term not in KNOWN_DIET_TERMS:
                if not any(term in ing for ing in available_ingredients):
                    available_ingredients.append(term)

    # Ensure context-resolved dish is included in search candidates
    if context_dish:
        clean_ctx = context_dish.lower().strip()
        if clean_ctx not in [i.lower() for i in available_ingredients]:
            available_ingredients.append(clean_ctx)

    return StructuredConstraints(
        intent="recipe_search",
        available_ingredients=available_ingredients,
        allergies=list(allergies_set),
        diet_type=diet_type,
        max_time_minutes=max_time,
        max_calories=max_cal,
        cuisine=cuisine,
        servings=2
    )

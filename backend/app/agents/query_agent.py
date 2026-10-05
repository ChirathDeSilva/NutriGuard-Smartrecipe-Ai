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
from typing import List, Optional
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

# Unrelated topics (tech, coding, politics, weather, finance, gaming, etc.)
UNRELATED_PATTERNS = [
    r"\b(?:weather|forecast|rain|temperature)\b",
    r"\b(?:stock|crypto|bitcoin|trading|forex|invest)\b",
    r"\b(?:code|python|java|javascript|c\+\+|programming|bug|sql|html)\b",
    r"\b(?:movie|film|song|music|actor|sports|football|cricket|game|gaming)\b",
    r"\b(?:politics|president|election|war)\b",
    r"\b(?:car|vehicle|repair|flight|hotel)\b"
]

# Culinary & recipe keywords
CULINARY_KEYWORDS = {
    "cook", "recipe", "curry", "dish", "make", "eat", "dinner", "lunch", "breakfast",
    "ingredient", "ingredients", "spices", "chicken", "lentils", "dhal", "rice", "curry",
    "sambol", "fish", "soup", "salad", "food", "calories", "bake", "fry", "boil"
}

# Stopwords/filler words that should not be parsed as ingredients
IGNORE_WORDS = {
    "recipe", "recipes", "food", "dinner", "lunch", "breakfast", "dish",
    "quick", "fast", "healthy", "meal", "something", "want", "have", "cook",
    "make", "give", "minutes", "mins", "calories", "kcal", "time", "sri lankan",
    "i", "me", "my", "we", "under", "about", "around", "less", "more", "need",
    "hi", "hello", "hey", "please", "can", "you", "tell", "show"
}


def parse_query(request: UserQueryRequest) -> StructuredConstraints:
    """
    Parses a UserQueryRequest into a StructuredConstraints object using NLP and regex.
    Combines user prompt text with sidebar widget selections.
    """
    prompt = request.prompt.strip()
    prompt_lower = prompt.lower()

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
    # 4. Intent Classification: greeting, unrelated, or recipe_search
    # --------------------------------------------------------------------------
    # Check for greeting or introductory question first
    is_greeting = any(re.search(pat, prompt_lower) for pat in GREETING_PATTERNS)
    # Check for explicitly unrelated topics
    is_unrelated = any(re.search(pat, prompt_lower) for pat in UNRELATED_PATTERNS)

    has_culinary = any(kw in prompt_lower for kw in CULINARY_KEYWORDS)

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

    # --------------------------------------------------------------------------
    # 5. Extract Ingredients via spaCy Noun Chunks
    # --------------------------------------------------------------------------
    available_ingredients: List[str] = []
    doc = nlp(prompt)

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

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ==============================================================================
# 1. API REQUEST CONTRACT (Frontend -> FastAPI Orchestrator)
# ==============================================================================
class UserQueryRequest(BaseModel):
    user_id: Optional[int] = 1
    prompt: str = Field(..., max_length=500, description="Raw user prompt capped at 500 characters")
    dietary_preferences: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    max_cooking_time: Optional[int] = None
    calorie_limit: Optional[float] = None
    cuisine_preference: Optional[str] = None


# ==============================================================================
# 2. AGENT 1 CONTRACT: Query Understanding (Agent 1 -> Agent 2)
# ==============================================================================
class StructuredConstraints(BaseModel):
    intent: str = "recipe_search"
    available_ingredients: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    diet_type: Optional[str] = None
    max_time_minutes: Optional[int] = None
    max_calories: Optional[float] = None
    cuisine: Optional[str] = None
    servings: int = 2


# ==============================================================================
# 3. AGENT 2 CONTRACT: Information Retrieval (Agent 2 -> Agent 3)
# ==============================================================================
class CandidateRecipe(BaseModel):
    id: str
    title: str
    ingredients: List[str]
    instructions: str
    cooking_minutes: int
    calories: float
    protein_grams: float
    carbs_grams: float = 0.0
    fat_grams: float = 0.0
    dietary_tags: List[str] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)
    cuisine: str
    popularity: float = 0.5
    source: str = "Local Knowledgebase"


# ==============================================================================
# 4. AGENT 3 CONTRACT: Safety & Nutrition Validation (Agent 3 -> Agent 4)
# ==============================================================================
class SafetyVerdict(BaseModel):
    recipe_id: str
    is_safe: bool
    violations: List[str] = Field(default_factory=list)


# ==============================================================================
# 5. AGENT 4 CONTRACT: Ranking & Scoring (Agent 4 -> Agent 5)
# ==============================================================================
class RankedRecipe(BaseModel):
    recipe: CandidateRecipe
    final_score: float
    score_breakdown: Dict[str, float]


# ==============================================================================
# 6. AGENT 5 CONTRACT: Final Grounded Response (Agent 5 -> Frontend)
# ==============================================================================
class FinalAgentResponse(BaseModel):
    recipe_title: str
    score: float
    why_selected: str
    formatted_instructions: str
    nutrition_facts: Dict[str, Any]
    warnings: List[str]
    sources: List[str]
    score_breakdown: Dict[str, float]
    is_nutrition_estimated: bool = False


# ==============================================================================
# 7. NEWS & TIPS CONTRACTS (Supporting Features)
# ==============================================================================
class NutritionTipCreate(BaseModel):
    title: str
    summary: str
    content: str
    category: str = "tip"  # "tip" or "news"
    author: Optional[str] = "NutriGuard Health Team"
    image_url: Optional[str] = None
    tags: Optional[str] = "nutrition,health"


class NutritionTipResponse(BaseModel):
    id: int
    title: str
    summary: str
    content: str
    category: str
    author: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[str] = None
    is_published: bool = True
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

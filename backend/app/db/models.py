from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.app.db.database import Base


def utcnow():
    return datetime.now(timezone.utc)


# 1. User Account Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    saved_recipes = relationship("SavedRecipe", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")


# 2. User Profile Preferences Table
class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diet_type = Column(String, nullable=True)                 # e.g., "vegan", "vegetarian"
    allergies = Column(Text, default="[]")                    # Stored as JSON string
    nutrition_goal = Column(String, nullable=True)            # e.g., "high_protein"
    daily_calorie_target = Column(Float, nullable=True)
    preferred_cuisines = Column(String, nullable=True)
    budget_level = Column(String, default="medium")
    language = Column(String, default="en")

    user = relationship("User", back_populates="profile")


# 3. Standard Allergen Definitions
class Allergen(Base):
    __tablename__ = "allergens"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # e.g., "peanuts", "fish"
    description = Column(String, nullable=True)

    aliases = relationship("IngredientAlias", back_populates="allergen")
    recipe_allergens = relationship("RecipeAllergen", back_populates="allergen")


# 4. Ingredient Synonyms & Allergen Mapping
class IngredientAlias(Base):
    __tablename__ = "ingredient_aliases"
    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, index=True, nullable=False)    # e.g., "fish"
    alias = Column(String, index=True, nullable=False)             # e.g., "maldive fish flakes"
    allergen_id = Column(Integer, ForeignKey("allergens.id"), nullable=True)

    allergen = relationship("Allergen", back_populates="aliases")


# 5. Core Recipes Table
class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, nullable=True)                   # ID if imported from TheMealDB
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    cuisine = Column(String, default="Sri Lankan")
    meal_type = Column(String, default="Dinner")
    instructions = Column(Text, nullable=False)
    preparation_minutes = Column(Integer, default=10)
    cooking_minutes = Column(Integer, default=20)
    servings = Column(Integer, default=2)
    source_name = Column(String, default="Local Knowledgebase")
    source_url = Column(String, nullable=True)
    source_type = Column(String, default="local")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    allergens = relationship("RecipeAllergen", back_populates="recipe", cascade="all, delete-orphan")
    nutrition = relationship("Nutrition", back_populates="recipe", uselist=False, cascade="all, delete-orphan")
    saved_by = relationship("SavedRecipe", back_populates="recipe")


# 6. Recipe Ingredients Table
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_name = Column(String, nullable=False)
    canonical_ingredient = Column(String, nullable=True)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="portion")
    is_optional = Column(Boolean, default=False)

    recipe = relationship("Recipe", back_populates="ingredients")


# 7. Recipe Allergen Link Table
class RecipeAllergen(Base):
    __tablename__ = "recipe_allergens"
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    allergen_id = Column(Integer, ForeignKey("allergens.id"), nullable=False)
    confidence = Column(Float, default=1.0)
    source = Column(String, default="deterministic_rule")

    recipe = relationship("Recipe", back_populates="allergens")
    allergen = relationship("Allergen", back_populates="recipe_allergens")


# 8. Nutrition Records Table
class Nutrition(Base):
    __tablename__ = "nutrition"
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    calories = Column(Float, nullable=False)
    protein_grams = Column(Float, nullable=False)
    carbs_grams = Column(Float, default=0.0)
    fat_grams = Column(Float, default=0.0)
    fiber_grams = Column(Float, default=0.0)
    sodium_mg = Column(Float, default=0.0)
    per_serving = Column(Boolean, default=True)
    source = Column(String, default="USDA / Local Standard")
    is_estimated = Column(Boolean, default=False)

    recipe = relationship("Recipe", back_populates="nutrition")


# 9. User Saved Recipes Table
class SavedRecipe(Base):
    __tablename__ = "saved_recipes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="saved_recipes")
    recipe = relationship("Recipe", back_populates="saved_by")


# 10. Chat Conversations & Messages Tables
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    conversation = relationship("Conversation", back_populates="messages")


# 11. Security Audit Logs Table
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    event_type = Column(String, nullable=False)        # e.g., "ALLERGEN_BLOCKED", "PROMPT_INJECTION"
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    status = Column(String, nullable=False)            # "SUCCESS" or "BLOCKED"
    ip_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    extra_metadata = Column(Text, nullable=True)       # Detailed JSON string of violation


# 12. Recipe Nutrition Tips & Food Safety News Table
class NutritionTip(Base):
    __tablename__ = "nutrition_tips"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, default="tip", index=True)       # "tip" (Nutrition Tip) or "news" (Food Safety News)
    author = Column(String, default="NutriGuard Health Team")
    image_url = Column(String, nullable=True)
    tags = Column(String, default="nutrition,health")          # Comma-separated tags
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


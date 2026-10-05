import os
import sys

# Ensure the root project directory is on the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.db.database import engine, SessionLocal, Base
from backend.app.db.models import (
    User,
    UserProfile,
    Allergen,
    IngredientAlias,
    Recipe,
    RecipeIngredient,
    RecipeAllergen,
    Nutrition,
    NutritionTip
)

def seed_database():
    print("Initializing database tables...")
    # 1. Inspect SQLAlchemy models and create all 11 tables in SQLite
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Prevent duplicate data insertion if database was already seeded
    if db.query(Recipe).first():
        print("Database already contains records. Seeding skipped.")
        db.close()
        return

    print("Seeding database with initial records...")

    try:
        # ==============================================================================
        # 1. Seed Demo User & Profile
        # ==============================================================================
        demo_user = User(
            email="student@sliit.lk",
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Hashed demo password
            role="user",
            is_active=True
        )
        db.add(demo_user)
        db.flush()  # Populates demo_user.id

        user_profile = UserProfile(
            user_id=demo_user.id,
            diet_type="none",
            allergies='["peanuts"]',
            nutrition_goal="balanced",
            daily_calorie_target=600.0,
            preferred_cuisines="Sri Lankan",
            budget_level="medium",
            language="en"
        )
        db.add(user_profile)

        # ==============================================================================
        # 2. Seed Common Standard Allergens
        # ==============================================================================
        allergens_list = ["Peanuts", "Dairy", "Eggs", "Gluten", "Fish", "Shellfish", "Soy", "Tree Nuts"]
        allergen_records = {}

        for allergen_name in allergens_list:
            obj = Allergen(
                name=allergen_name, 
                description=f"Standard food allergen: {allergen_name}"
            )
            db.add(obj)
            allergen_records[allergen_name.lower()] = obj

        db.flush()

        # ==============================================================================
        # 3. Seed Ingredient Aliases
        # ==============================================================================
        aliases_data = [
            ("fish", "maldive fish flakes", allergen_records["fish"].id),
            ("fish", "tuna flakes", allergen_records["fish"].id),
            ("dairy", "cow milk", allergen_records["dairy"].id),
            ("dairy", "butter", allergen_records["dairy"].id),
            ("gluten", "wheat flour", allergen_records["gluten"].id),
            ("peanuts", "groundnuts", allergen_records["peanuts"].id)
        ]

        for canonical, alias_name, a_id in aliases_data:
            db.add(IngredientAlias(
                canonical_name=canonical,
                alias=alias_name,
                allergen_id=a_id
            ))

        # ==============================================================================
        # 4. Seed Sri Lankan Recipes
        # ==============================================================================

        # --- Recipe 1: Sri Lankan Dhal Curry (Vegan, Allergen-Free) ---
        dhal = Recipe(
            title="Sri Lankan Dhal Curry (Parippu)",
            description="Comforting red lentils cooked with coconut milk, tempered with spices.",
            cuisine="Sri Lankan",
            meal_type="Dinner",
            cooking_minutes=25,
            preparation_minutes=5,
            servings=2,
            instructions=(
                "1. Rinse red lentils thoroughly in cold water.\n"
                "2. Simmer lentils with water, turmeric, and sliced onions until tender.\n"
                "3. Stir in coconut milk and gently simmer for 5 minutes.\n"
                "4. In a separate pan, temper mustard seeds and curry leaves in hot oil, then fold into the curry."
            ),
            source_name="Local Knowledgebase",
            source_type="local"
        )
        db.add(dhal)
        db.flush()

        # Nutrition for Dhal
        db.add(Nutrition(
            recipe_id=dhal.id,
            calories=280.0,
            protein_grams=14.0,
            carbs_grams=38.0,
            fat_grams=8.0,
            fiber_grams=9.0,
            sodium_mg=340.0,
            per_serving=True,
            is_estimated=False
        ))

        # Ingredients for Dhal
        dhal_ingredients = [
            ("red lentils", "red lentils", 1.0, "cup"),
            ("coconut milk", "coconut milk", 0.5, "cup"),
            ("turmeric", "turmeric powder", 0.5, "tsp"),
            ("curry leaves", "curry leaves", 1.0, "sprig"),
            ("mustard seeds", "mustard seeds", 0.5, "tsp"),
            ("onion", "red onion", 0.5, "piece")
        ]
        for name, canonical, qty, unit in dhal_ingredients:
            db.add(RecipeIngredient(
                recipe_id=dhal.id,
                ingredient_name=name,
                canonical_ingredient=canonical,
                quantity=qty,
                unit=unit
            ))

        # --- Recipe 2: Spicy Pol Sambol (Contains Fish Allergen) ---
        sambol = Recipe(
            title="Spicy Pol Sambol",
            description="Traditional fresh coconut relish with chili, shallots, and fish flakes.",
            cuisine="Sri Lankan",
            meal_type="Side Dish",
            cooking_minutes=10,
            preparation_minutes=5,
            servings=2,
            instructions=(
                "1. Grind red chili powder, salt, and shallots together using a pestle or small processor.\n"
                "2. Mix in fresh grated coconut and Maldive fish flakes.\n"
                "3. Thoroughly mix by hand and finish with freshly squeezed lime juice."
            ),
            source_name="Local Knowledgebase",
            source_type="local"
        )
        db.add(sambol)
        db.flush()

        # Nutrition for Pol Sambol
        db.add(Nutrition(
            recipe_id=sambol.id,
            calories=190.0,
            protein_grams=4.0,
            carbs_grams=8.0,
            fat_grams=16.0,
            fiber_grams=4.0,
            sodium_mg=280.0,
            per_serving=True,
            is_estimated=False
        ))

        # Ingredients for Pol Sambol
        sambol_ingredients = [
            ("fresh grated coconut", "coconut", 1.0, "cup"),
            ("red chili powder", "chili powder", 1.0, "tbsp"),
            ("shallots", "shallots", 4.0, "pieces"),
            ("lime juice", "lime", 1.0, "tbsp"),
            ("salt", "salt", 0.5, "tsp"),
            ("maldive fish flakes", "fish", 1.0, "tsp")
        ]
        for name, canonical, qty, unit in sambol_ingredients:
            db.add(RecipeIngredient(
                recipe_id=sambol.id,
                ingredient_name=name,
                canonical_ingredient=canonical,
                quantity=qty,
                unit=unit
            ))

        # Link Fish allergen flag to Pol Sambol (Used for Deterministic Rejection in Agent 3)
        db.add(RecipeAllergen(
            recipe_id=sambol.id,
            allergen_id=allergen_records["fish"].id,
            confidence=1.0,
            source="deterministic_rule"
        ))

        # --- Recipe 3: Sri Lankan Chicken Curry (Gluten-Free, Dairy-Free) ---
        chicken = Recipe(
            title="Sri Lankan Chicken Curry",
            description="Tender chicken pieces simmered in roasted curry powder and coconut gravy.",
            cuisine="Sri Lankan",
            meal_type="Dinner",
            cooking_minutes=35,
            preparation_minutes=10,
            servings=3,
            instructions=(
                "1. Marinate chicken pieces with roasted curry powder, turmeric, and salt.\n"
                "2. Saute onions, garlic, ginger, and curry leaves in hot coconut oil until fragrant.\n"
                "3. Add chicken pieces and sear for 5 minutes until sealed.\n"
                "4. Pour in coconut milk and water, simmering on low heat until cooked through."
            ),
            source_name="Local Knowledgebase",
            source_type="local"
        )
        db.add(chicken)
        db.flush()

        # Nutrition for Chicken Curry
        db.add(Nutrition(
            recipe_id=chicken.id,
            calories=380.0,
            protein_grams=32.0,
            carbs_grams=6.0,
            fat_grams=24.0,
            fiber_grams=2.0,
            sodium_mg=450.0,
            per_serving=True,
            is_estimated=False
        ))

        # Ingredients for Chicken Curry
        chicken_ingredients = [
            ("chicken pieces", "chicken", 400.0, "g"),
            ("roasted curry powder", "curry powder", 1.5, "tbsp"),
            ("coconut milk", "coconut milk", 0.75, "cup"),
            ("red onion", "onion", 1.0, "piece"),
            ("garlic", "garlic", 3.0, "cloves"),
            ("ginger", "ginger", 1.0, "inch"),
            ("curry leaves", "curry leaves", 1.0, "sprig")
        ]
        for name, canonical, qty, unit in chicken_ingredients:
            db.add(RecipeIngredient(
                recipe_id=chicken.id,
                ingredient_name=name,
                canonical_ingredient=canonical,
                quantity=qty,
                unit=unit
            ))

        # --- Recipe 4: Traditional Sri Lankan Pol Roti (Coconut Flatbread) ---
        roti = Recipe(
            title="Sri Lankan Pol Roti (Coconut Roti)",
            description="Traditional rustic Sri Lankan flatbread made with wheat flour, freshly scraped coconut, and mild green chilies.",
            cuisine="Sri Lankan",
            meal_type="Breakfast",
            cooking_minutes=20,
            preparation_minutes=10,
            servings=4,
            instructions=(
                "1. In a large bowl, mix wheat flour, scraped fresh coconut, chopped shallots, green chilies, and salt.\n"
                "2. Gradually add warm water and knead into a soft, non-sticky dough ball.\n"
                "3. Divide dough into 4 balls, flatten each into round discs about 1/4 inch thick.\n"
                "4. Cook on a dry heavy pan or griddle on medium heat for 3-4 minutes on each side until golden brown spots appear.\n"
                "5. Serve warm with spicy Lunu Miris, Pol Sambol, or Dhal curry."
            ),
            source_name="Local Knowledgebase",
            source_type="local"
        )
        db.add(roti)
        db.flush()

        # Nutrition for Pol Roti
        db.add(Nutrition(
            recipe_id=roti.id,
            calories=230.0,
            protein_grams=6.0,
            carbs_grams=34.0,
            fat_grams=8.0,
            fiber_grams=4.0,
            sodium_mg=210.0,
            per_serving=True,
            is_estimated=False
        ))

        # Ingredients for Pol Roti
        roti_ingredients = [
            ("wheat flour", "wheat flour", 2.0, "cups"),
            ("fresh grated coconut", "coconut", 1.0, "cup"),
            ("red shallots", "shallots", 3.0, "pieces"),
            ("green chilies", "chili", 2.0, "pieces"),
            ("salt", "salt", 1.0, "tsp"),
            ("warm water", "water", 0.75, "cup")
        ]
        for name, canonical, qty, unit in roti_ingredients:
            db.add(RecipeIngredient(
                recipe_id=roti.id,
                ingredient_name=name,
                canonical_ingredient=canonical,
                quantity=qty,
                unit=unit
            ))

        # Link Gluten allergen to Pol Roti (Wheat flour contains gluten)
        db.add(RecipeAllergen(
            recipe_id=roti.id,
            allergen_id=allergen_records["gluten"].id,
            confidence=1.0,
            source="deterministic_rule"
        ))

        # ==============================================================================
        # 5. Seed Recipe Nutrition Tips & Food Safety News
        # ==============================================================================
        print("Seeding curated nutrition tips and food safety news...")
        tips_data = [
            NutritionTip(
                title="The Healing Power of Turmeric in Sri Lankan Cuisine",
                summary="Why adding turmeric and black pepper together maximizes bioavailability and anti-inflammatory benefits.",
                content=(
                    "Turmeric (Kaha) has been a staple of Sri Lankan culinary tradition for centuries. "
                    "Its active compound, curcumin, is renowned for potent anti-inflammatory and antioxidant properties. "
                    "However, curcumin alone has low absorption in the human bloodstream. When cooked alongside black pepper "
                    "(piperine) and healthy fats like coconut milk in curries, its bioavailability skyrockets by up to 2000%! "
                    "Tip: Add a pinch of black pepper whenever tempering or stewing turmeric-rich dishes."
                ),
                category="tip",
                author="Dr. Anoma Jayasinghe (Clinical Nutritionist)",
                tags="turmeric,anti-inflammatory,curry,spices",
                is_published=True
            ),
            NutritionTip(
                title="The Sri Lankan Balanced Plate Method",
                summary="How to balance rice-and-curry meals with optimum protein and fiber ratios.",
                content=(
                    "Traditional Sri Lankan meals are rich in flavor but can often become carb-heavy if rice portions are uncontrolled. "
                    "To achieve optimal metabolic health: fill 1/2 of your plate with high-fiber vegetables and greens (like Gotu Kola or Mukunuwenna), "
                    "1/4 with lean protein (fish, eggs, dhal, or chicken), and 1/4 with complex carbohydrates (red rice, brown rice, or kurakkan). "
                    "This prevents post-meal glucose spikes and keeps you satiated for hours."
                ),
                category="tip",
                author="NutriGuard Health Team",
                tags="balanced-diet,macronutrients,rice,protein",
                is_published=True
            ),
            NutritionTip(
                title="2026 Food Allergen Safety: Hidden Sources in Everyday Dining",
                summary="Essential guide to spotting hidden allergens like fish flakes, gluten cross-contact, and peanut oils.",
                content=(
                    "Food allergies affect millions worldwide. In South Asian cuisine, common hidden allergens include Maldive fish "
                    "(often added to sambols and vegetable curries for umami flavor), hing/asafoetida mixed with wheat flour (gluten), "
                    "and unrefined peanut or sesame tempering oils. Always verify ingredient lists or request allergen-free preparations "
                    "when cooking at home or eating out."
                ),
                category="news",
                author="Food Safety Standards Board",
                tags="allergens,food-safety,celiac,peanut-free",
                is_published=True
            ),
            NutritionTip(
                title="Smart Sodium Reduction: Enhancing Flavor with Lime & Spices",
                summary="Cut down table salt without sacrificing authentic flavor using roasted spices and citrus.",
                content=(
                    "Excess sodium intake is a leading contributor to hypertension. You can easily cut sodium by 30-40% in curries "
                    "by leveraging roasted curry powder, goraka (Garcinia cambogia), tamarind, and fresh lime juice. "
                    "Acidic notes trick the palate into perceiving higher salinity, allowing you to use less table salt while enjoying full, vibrant flavors."
                ),
                category="tip",
                author="Chef Ranil Fernando",
                tags="sodium,heart-health,spices,lime",
                is_published=True
            )
        ]

        for tip in tips_data:
            db.add(tip)

        # Commit everything to the SQLite database
        db.commit()
        db.close()
        print("Database seeding completed successfully! Database created at backend/data/recipes.db")

    except Exception as e:
        db.rollback()
        db.close()
        print(f"Error seeding database: {e}")
        raise e

if __name__ == "__main__":
    seed_database()

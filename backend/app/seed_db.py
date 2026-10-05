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


def seed_database(force: bool = False):
    print("Initializing database tables...")
    if force:
        print("Force re-seeding: dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if not force and db.query(Recipe).first():
        print("Database already contains records. Seeding skipped. (Use --force to overwrite)")
        db.close()
        return

    print("Seeding database with authentic Sri Lankan recipes & safety data...")

    try:
        # ==============================================================================
        # 1. Seed Demo User & Profile
        # ==============================================================================
        demo_user = User(
            email="student@sliit.lk",
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            role="user",
            is_active=True
        )
        db.add(demo_user)
        db.flush()

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
        allergens_list = ["Peanuts", "Dairy", "Eggs", "Gluten", "Fish", "Shellfish", "Soy", "Tree Nuts", "Sesame"]
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
            ("fish", "sprats", allergen_records["fish"].id),
            ("shellfish", "prawns", allergen_records["shellfish"].id),
            ("shellfish", "crab meat", allergen_records["shellfish"].id),
            ("dairy", "cow milk", allergen_records["dairy"].id),
            ("dairy", "butter", allergen_records["dairy"].id),
            ("dairy", "ghee", allergen_records["dairy"].id),
            ("gluten", "wheat flour", allergen_records["gluten"].id),
            ("gluten", "godamba roti", allergen_records["gluten"].id),
            ("peanuts", "groundnuts", allergen_records["peanuts"].id),
            ("tree nuts", "cashew nuts", allergen_records["tree nuts"].id),
            ("soy", "soy sauce", allergen_records["soy"].id),
            ("sesame", "sesame oil", allergen_records["sesame"].id)
        ]

        for canonical, alias_name, a_id in aliases_data:
            db.add(IngredientAlias(
                canonical_name=canonical,
                alias=alias_name,
                allergen_id=a_id
            ))

        # Helper function to insert a complete recipe
        def add_full_recipe(r_dict, nutr_dict, ingredients_list, allergen_keys=None):
            recipe_obj = Recipe(
                title=r_dict["title"],
                description=r_dict["description"],
                cuisine=r_dict.get("cuisine", "Sri Lankan"),
                meal_type=r_dict.get("meal_type", "Dinner"),
                cooking_minutes=r_dict["cooking_minutes"],
                preparation_minutes=r_dict.get("preparation_minutes", 10),
                servings=r_dict.get("servings", 2),
                instructions=r_dict["instructions"],
                source_name=r_dict.get("source_name", "Local Knowledgebase"),
                source_type="local"
            )
            db.add(recipe_obj)
            db.flush()

            db.add(Nutrition(
                recipe_id=recipe_obj.id,
                calories=nutr_dict["calories"],
                protein_grams=nutr_dict["protein"],
                carbs_grams=nutr_dict["carbs"],
                fat_grams=nutr_dict["fat"],
                fiber_grams=nutr_dict.get("fiber", 3.0),
                sodium_mg=nutr_dict.get("sodium", 300.0),
                per_serving=True,
                is_estimated=False
            ))

            for item in ingredients_list:
                name, canonical, qty, unit = item
                db.add(RecipeIngredient(
                    recipe_id=recipe_obj.id,
                    ingredient_name=name,
                    canonical_ingredient=canonical,
                    quantity=qty,
                    unit=unit
                ))

            if allergen_keys:
                for a_key in allergen_keys:
                    norm_k = a_key.lower()
                    if norm_k in allergen_records:
                        db.add(RecipeAllergen(
                            recipe_id=recipe_obj.id,
                            allergen_id=allergen_records[norm_k].id,
                            confidence=1.0,
                            source="deterministic_rule"
                        ))

            return recipe_obj

        # ==============================================================================
        # 4. Seed Authentic Sri Lankan Recipes (20 Dishes)
        # ==============================================================================

        # 1. Sri Lankan Dhal Curry (Parippu) - Naturally Vegan, Gluten-Free
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Dhal Curry (Parippu)",
                "description": "Heartwarming red lentils simmered in velvety coconut milk, fragrant curry leaves, turmeric, and tempered mustard seeds.",
                "meal_type": "Dinner",
                "cooking_minutes": 25,
                "preparation_minutes": 5,
                "servings": 2,
                "instructions": (
                    "1. Rinse red lentils thoroughly in cold water until water runs clear.\n"
                    "2. Simmer lentils in a saucepan with water, sliced shallots, turmeric powder, green chili, and curry leaves until soft.\n"
                    "3. Pour in thick coconut milk, season with salt, and simmer gently on low heat for 5 minutes.\n"
                    "4. In a separate small frying pan, temper mustard seeds, sliced garlic, and curry leaves in coconut oil until popping.\n"
                    "5. Pour hot tempered spice oil into the dhal curry, stir well, and serve hot."
                )
            },
            nutr_dict={"calories": 280.0, "protein": 14.0, "carbs": 38.0, "fat": 8.0, "fiber": 9.0, "sodium": 340.0},
            ingredients_list=[
                ("red lentils", "red lentils", 1.0, "cup"),
                ("coconut milk", "coconut milk", 0.75, "cup"),
                ("turmeric powder", "turmeric", 0.5, "tsp"),
                ("curry leaves", "curry leaves", 1.0, "sprig"),
                ("mustard seeds", "mustard seeds", 0.5, "tsp"),
                ("shallots", "shallots", 4.0, "pieces"),
                ("garlic", "garlic", 2.0, "cloves")
            ]
        )

        # 2. Spicy Pol Sambol - Contains Fish (Maldive fish)
        add_full_recipe(
            r_dict={
                "title": "Spicy Pol Sambol",
                "description": "Vibrant and zesty freshly grated coconut relish crushed with whole red chili, shallots, lime, and umami Maldive fish flakes.",
                "meal_type": "Side Dish",
                "cooking_minutes": 10,
                "preparation_minutes": 5,
                "servings": 2,
                "instructions": (
                    "1. Grind red chili powder, salt, and peeled shallots together in a mortar and pestle or spice grinder into a coarse paste.\n"
                    "2. Add freshly scraped coconut and pounded Maldive fish flakes.\n"
                    "3. Mix and massage thoroughly by hand until the coconut absorbs the deep red chili hue.\n"
                    "4. Squeeze in fresh lime juice to taste and serve immediately with hot rice, hoppers, or pol roti."
                )
            },
            nutr_dict={"calories": 190.0, "protein": 4.0, "carbs": 8.0, "fat": 16.0, "fiber": 4.0, "sodium": 280.0},
            ingredients_list=[
                ("fresh grated coconut", "coconut", 1.0, "cup"),
                ("red chili powder", "chili powder", 1.0, "tbsp"),
                ("shallots", "shallots", 4.0, "pieces"),
                ("lime juice", "lime", 1.0, "tbsp"),
                ("salt", "salt", 0.5, "tsp"),
                ("maldive fish flakes", "fish", 1.0, "tsp")
            ],
            allergen_keys=["fish"]
        )

        # 3. Sri Lankan Chicken Curry (Kukul Mas Curry)
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Chicken Curry",
                "description": "Tender bone-in chicken simmered in rich dark roasted Ceylon curry powder, pandan leaves, lemongrass, and creamy coconut milk.",
                "meal_type": "Dinner",
                "cooking_minutes": 35,
                "preparation_minutes": 10,
                "servings": 3,
                "instructions": (
                    "1. Marinate chicken pieces with roasted Ceylon curry powder, turmeric, black pepper, and salt for 15 minutes.\n"
                    "2. Heat coconut oil in a clay pot or heavy pan. Sauté sliced red onions, garlic, ginger, curry leaves, and pandan leaf until fragrant.\n"
                    "3. Add chicken pieces and sear over medium-high heat for 5 minutes until sealed.\n"
                    "4. Pour in thin coconut milk, cover, and gently simmer for 20 minutes until chicken is tender.\n"
                    "5. Pour in 1/2 cup of thick coconut milk, simmer for 5 more minutes until the gravy turns rich and aromatic."
                )
            },
            nutr_dict={"calories": 380.0, "protein": 32.0, "carbs": 6.0, "fat": 24.0, "fiber": 2.0, "sodium": 450.0},
            ingredients_list=[
                ("chicken pieces", "chicken", 450.0, "g"),
                ("roasted curry powder", "curry powder", 1.5, "tbsp"),
                ("coconut milk", "coconut milk", 1.0, "cup"),
                ("red onion", "onion", 1.0, "piece"),
                ("garlic", "garlic", 3.0, "cloves"),
                ("ginger", "ginger", 1.0, "inch"),
                ("curry leaves", "curry leaves", 1.0, "sprig"),
                ("pandan leaf", "pandan", 1.0, "piece")
            ]
        )

        # 4. Traditional Sri Lankan Pol Roti - Contains Gluten
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Pol Roti (Coconut Roti)",
                "description": "Rustic, hearty Sri Lankan flatbread made with wheat flour, freshly scraped coconut, diced shallots, and spicy green chilies.",
                "meal_type": "Breakfast",
                "cooking_minutes": 20,
                "preparation_minutes": 10,
                "servings": 4,
                "instructions": (
                    "1. In a large mixing bowl, combine wheat flour, fresh grated coconut, diced shallots, chopped green chilies, and salt.\n"
                    "2. Gradually add warm water while kneading until a soft, pliable, non-sticky dough forms.\n"
                    "3. Divide dough into 4 equal balls. Flatten each ball with your palms on a lightly floured surface into 1/4-inch discs.\n"
                    "4. Heat a dry iron griddle or skillet over medium heat. Toast each roti for 3-4 minutes per side until golden brown spots appear.\n"
                    "5. Serve piping hot with spicy Lunu Miris, Pol Sambol, or Dhal curry."
                )
            },
            nutr_dict={"calories": 230.0, "protein": 6.0, "carbs": 34.0, "fat": 8.0, "fiber": 4.0, "sodium": 210.0},
            ingredients_list=[
                ("wheat flour", "wheat flour", 2.0, "cups"),
                ("fresh grated coconut", "coconut", 1.0, "cup"),
                ("shallots", "shallots", 3.0, "pieces"),
                ("green chilies", "chili", 2.0, "pieces"),
                ("salt", "salt", 1.0, "tsp"),
                ("warm water", "water", 0.75, "cup")
            ],
            allergen_keys=["gluten"]
        )

        # 5. Sri Lankan Vegetable & Egg Kottu Roti - Contains Gluten & Eggs
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Vegetable & Egg Kottu Roti",
                "description": "Famous street-food spectacle of chopped Godamba flatbread stir-fried on an iron griddle with fresh vegetables, eggs, and aromatic curry spices.",
                "meal_type": "Dinner",
                "cooking_minutes": 15,
                "preparation_minutes": 10,
                "servings": 2,
                "instructions": (
                    "1. Cut Godamba flatbread or parathas into thin, bite-sized ribbons.\n"
                    "2. Heat vegetable oil in a large wok or skillet. Sauté onions, garlic, ginger, curry leaves, and green chilies.\n"
                    "3. Toss in shredded cabbage, carrots, and leeks; stir-fry vigorously on high heat for 3 minutes.\n"
                    "4. Push veggies aside, crack two fresh eggs into the pan, and scramble until softly set.\n"
                    "5. Add the shredded roti strips, Ceylon curry powder, chili flakes, and 3 tablespoons of rich curry gravy.\n"
                    "6. Stir-fry and rhythmically chop with spatulas until thoroughly blended and piping hot."
                )
            },
            nutr_dict={"calories": 420.0, "protein": 15.0, "carbs": 54.0, "fat": 16.0, "fiber": 5.0, "sodium": 460.0},
            ingredients_list=[
                ("godamba roti strips", "wheat flour", 3.0, "sheets"),
                ("shredded cabbage", "cabbage", 1.0, "cup"),
                ("sliced carrots", "carrots", 0.5, "cup"),
                ("sliced leeks", "leeks", 0.5, "cup"),
                ("fresh eggs", "eggs", 2.0, "pieces"),
                ("curry leaves", "curry leaves", 1.0, "sprig"),
                ("roasted curry powder", "curry powder", 1.0, "tbsp"),
                ("vegetable oil", "oil", 2.0, "tbsp")
            ],
            allergen_keys=["gluten", "eggs"]
        )

        # 6. Sri Lankan Plain Hoppers (Appa) - Naturally Allergen-Free & Vegan
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Plain Hoppers (Appa)",
                "description": "Crispy bowl-shaped fermented coconut pancakes with a golden lacy rim and a soft, spongy cloud-like center.",
                "meal_type": "Breakfast",
                "cooking_minutes": 15,
                "preparation_minutes": 15,
                "servings": 4,
                "instructions": (
                    "1. Whisk rice flour, coconut water, a pinch of sugar, and active yeast; leave to ferment for 6 hours.\n"
                    "2. Whisk in rich coconut milk and salt to form a smooth, pourable batter.\n"
                    "3. Heat a rounded hopper pan (thachchiya). Pour a ladle of batter directly into the center.\n"
                    "4. Swirl the pan in a smooth circular motion to coat the sides, leaving a thick puddle in the center.\n"
                    "5. Cover with a lid and cook on medium flame for 2-3 minutes until edges become crisp and golden brown.\n"
                    "6. Gently slide onto a platter and serve with spicy Pol Sambol or Seeni Sambol."
                )
            },
            nutr_dict={"calories": 190.0, "protein": 3.5, "carbs": 34.0, "fat": 5.0, "fiber": 2.0, "sodium": 120.0},
            ingredients_list=[
                ("rice flour", "rice flour", 2.0, "cups"),
                ("thick coconut milk", "coconut milk", 1.0, "cup"),
                ("active dry yeast", "yeast", 1.0, "tsp"),
                ("coconut water", "water", 0.5, "cup"),
                ("salt", "salt", 0.5, "tsp")
            ]
        )

        # 7. Fish Ambul Thiyal (Southern Sour Fish Curry) - Contains Fish
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Fish Ambul Thiyal (Sour Fish Curry)",
                "description": "Iconic Southern Sri Lankan dry fish curry prepared with Goraka paste, crushed black pepper, and firm tuna, slow-simmered in a clay pot.",
                "meal_type": "Dinner",
                "cooking_minutes": 35,
                "preparation_minutes": 15,
                "servings": 3,
                "instructions": (
                    "1. Cut firm tuna or sailfish into 1-inch cubes and wash thoroughly with turmeric and lime.\n"
                    "2. Soak Goraka (Garcinia cambogia) in warm water and grind into a smooth dark paste with black pepper and salt.\n"
                    "3. Coat each fish cube generously in the thick Goraka and black pepper spice marinade.\n"
                    "4. Line the bottom of a clay pot with banana leaf or curry leaves and tightly arrange the fish pieces.\n"
                    "5. Pour in 1/2 cup water, cover tightly, and simmer on low heat for 30 minutes until water completely evaporates and gravy coats the fish.\n"
                    "6. Rest for at least 30 minutes before serving to allow deep spice penetration."
                )
            },
            nutr_dict={"calories": 250.0, "protein": 36.0, "carbs": 4.0, "fat": 9.0, "fiber": 2.0, "sodium": 380.0},
            ingredients_list=[
                ("tuna fish steaks", "fish", 400.0, "g"),
                ("goraka paste", "goraka", 3.0, "tbsp"),
                ("crushed black pepper", "black pepper", 1.5, "tbsp"),
                ("curry leaves", "curry leaves", 2.0, "sprigs"),
                ("pandan leaf", "pandan", 1.0, "piece"),
                ("salt", "salt", 1.0, "tsp")
            ],
            allergen_keys=["fish"]
        )

        # 8. Sri Lankan Cashew Nut Curry (Kaju Curry) - Contains Tree Nuts, Vegan
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Cashew Nut Curry (Kaju Curry)",
                "description": "Luxurious, creamy celebratory curry of tender whole raw cashews and sweet green peas simmered in mild coconut milk and aromatic Ceylon spices.",
                "meal_type": "Dinner",
                "cooking_minutes": 30,
                "preparation_minutes": 20,
                "servings": 3,
                "instructions": (
                    "1. Soak raw cashew nuts in hot water for 30 minutes to soften and plump up.\n"
                    "2. In a saucepan, combine softened cashews, green peas, sliced onions, garlic, turmeric, unroasted curry powder, and pandan leaf.\n"
                    "3. Add thin coconut milk, cover, and gently simmer for 20 minutes until cashews are buttery and tender.\n"
                    "4. Pour in rich thick coconut milk, season with salt, and simmer uncovered for 5 minutes until sauce thickens.\n"
                    "5. Serve warm alongside Yellow Rice or Pol Roti."
                )
            },
            nutr_dict={"calories": 360.0, "protein": 11.0, "carbs": 22.0, "fat": 26.0, "fiber": 4.0, "sodium": 240.0},
            ingredients_list=[
                ("raw cashew nuts", "cashew nuts", 200.0, "g"),
                ("coconut milk", "coconut milk", 1.0, "cup"),
                ("green peas", "peas", 0.5, "cup"),
                ("shallots", "shallots", 4.0, "pieces"),
                ("garlic", "garlic", 2.0, "cloves"),
                ("turmeric powder", "turmeric", 0.5, "tsp"),
                ("pandan leaf", "pandan", 1.0, "piece")
            ],
            allergen_keys=["tree nuts"]
        )

        # 9. Sri Lankan Tender Jackfruit Curry (Polos Curry) - Vegan, High Fiber
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Jackfruit Curry (Polos Curry)",
                "description": "Traditional slow-cooked young jackfruit curry with a meaty texture, roasted curry powder, and dark spiced coconut gravy.",
                "meal_type": "Lunch",
                "cooking_minutes": 45,
                "preparation_minutes": 15,
                "servings": 4,
                "instructions": (
                    "1. Peel and cube baby jackfruit into bite-sized chunks; rinse in turmeric water.\n"
                    "2. Toss jackfruit pieces with roasted Ceylon curry powder, chili powder, black pepper, and salt.\n"
                    "3. In a clay pot, sauté shallots, garlic, ginger, curry leaves, and a piece of Goraka in coconut oil.\n"
                    "4. Add the marinated jackfruit and thin coconut milk; cover and slow-simmer on low heat for 35 minutes.\n"
                    "5. Add thick coconut milk and simmer until jackfruit is fork-tender and gravy is rich and dark mahogany."
                )
            },
            nutr_dict={"calories": 210.0, "protein": 5.0, "carbs": 32.0, "fat": 7.0, "fiber": 8.0, "sodium": 290.0},
            ingredients_list=[
                ("young green jackfruit", "jackfruit", 400.0, "g"),
                ("coconut milk", "coconut milk", 1.25, "cups"),
                ("roasted curry powder", "curry powder", 1.5, "tbsp"),
                ("goraka", "goraka", 2.0, "pieces"),
                ("shallots", "shallots", 4.0, "pieces"),
                ("curry leaves", "curry leaves", 1.0, "sprig")
            ]
        )

        # 10. Sri Lankan Egg Curry (Bittara Curry) - Contains Eggs
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Egg Curry (Bittara Curry)",
                "description": "Golden pan-fried hard-boiled eggs scored and gently braised in a savory, spiced coconut gravy with onions and tomatoes.",
                "meal_type": "Dinner",
                "cooking_minutes": 20,
                "preparation_minutes": 10,
                "servings": 2,
                "instructions": (
                    "1. Hard-boil eggs, peel shells, and make 3 shallow lengthwise slits around each egg.\n"
                    "2. Dust eggs with turmeric and a pinch of salt; lightly sear in hot oil for 2 minutes until blisters form on the white.\n"
                    "3. In the same pan, sauté sliced onions, tomatoes, green chilies, curry leaves, and garlic.\n"
                    "4. Stir in Ceylon curry powder and pour in coconut milk; bring to a gentle boil.\n"
                    "5. Add the seared eggs into the bubbling gravy and simmer for 5 minutes so eggs absorb the spices."
                )
            },
            nutr_dict={"calories": 270.0, "protein": 14.0, "carbs": 7.0, "fat": 20.0, "fiber": 2.0, "sodium": 330.0},
            ingredients_list=[
                ("hard boiled eggs", "eggs", 4.0, "pieces"),
                ("coconut milk", "coconut milk", 0.75, "cup"),
                ("red onion", "onion", 1.0, "piece"),
                ("ripe tomato", "tomato", 1.0, "piece"),
                ("curry powder", "curry powder", 1.0, "tbsp"),
                ("turmeric", "turmeric", 0.5, "tsp"),
                ("curry leaves", "curry leaves", 1.0, "sprig")
            ],
            allergen_keys=["eggs"]
        )

        # 11. Sri Lankan Brinjal Moju (Wambatu Moju) - Vegan, Gluten-Free
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Brinjal Moju (Wambatu Moju)",
                "description": "Sweet, tangy, and deeply spiced caramelized eggplant pickle prepared with fried shallots, green chilies, mustard paste, and vinegar.",
                "meal_type": "Side Dish",
                "cooking_minutes": 25,
                "preparation_minutes": 15,
                "servings": 4,
                "instructions": (
                    "1. Cut eggplants into thin finger-sized strips, toss with turmeric and salt, and deep fry until crispy and dark golden brown.\n"
                    "2. Deep fry whole peeled shallots and whole green chilies until blistered.\n"
                    "3. In a small pot, simmer vinegar, coconut sugar, ground mustard paste, and chili powder until a thick syrupy dressing forms.\n"
                    "4. Turn off heat; fold in fried eggplant strips, fried shallots, and green chilies.\n"
                    "5. Toss gently until glossy and well-coated. Best served cooled with fragrant rice."
                )
            },
            nutr_dict={"calories": 180.0, "protein": 2.5, "carbs": 24.0, "fat": 9.0, "fiber": 5.0, "sodium": 260.0},
            ingredients_list=[
                ("eggplant brinjal", "eggplant", 350.0, "g"),
                ("shallots", "shallots", 8.0, "pieces"),
                ("green chilies", "chili", 4.0, "pieces"),
                ("mustard paste", "mustard", 1.0, "tbsp"),
                ("white vinegar", "vinegar", 3.0, "tbsp"),
                ("coconut sugar", "sugar", 1.5, "tbsp")
            ]
        )

        # 12. Sri Lankan Pennywort Salad (Gotu Kola Sambol) - Superfood Herbal Salad
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Pennywort Salad (Gotu Kola Sambol)",
                "description": "Nutrient-packed raw herbal salad made from finely shredded Centella asiatica (Gotu Kola), freshly scraped coconut, shallots, and lime.",
                "meal_type": "Side Dish",
                "cooking_minutes": 5,
                "preparation_minutes": 10,
                "servings": 2,
                "instructions": (
                    "1. Wash Gotu Kola leaves thoroughly and drain completely on paper towels.\n"
                    "2. Finely shred the leaves using a sharp chef's knife.\n"
                    "3. In a salad bowl, toss shredded Gotu Kola with freshly scraped coconut, sliced shallots, and diced green chilies.\n"
                    "4. Season with salt, freshly ground black pepper, and a generous squeeze of fresh lime juice.\n"
                    "5. Toss lightly right before serving to maintain crispness and vital nutrients."
                )
            },
            nutr_dict={"calories": 110.0, "protein": 3.0, "carbs": 6.0, "fat": 8.0, "fiber": 4.0, "sodium": 140.0},
            ingredients_list=[
                ("gotu kola leaves", "gotu kola", 2.0, "bunches"),
                ("fresh grated coconut", "coconut", 0.5, "cup"),
                ("shallots", "shallots", 3.0, "pieces"),
                ("fresh lime juice", "lime", 1.0, "tbsp"),
                ("salt", "salt", 0.5, "tsp"),
                ("green chili", "chili", 1.0, "piece")
            ]
        )

        # 13. Sri Lankan Jaffna Prawn Curry (Isso Curry) - Contains Shellfish
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Jaffna Prawn Curry (Isso Curry)",
                "description": "Plump juicy prawns gently simmered in fiery Jaffna roasted curry powder, fenugreek seeds, tamarind extract, and rich coconut milk.",
                "meal_type": "Dinner",
                "cooking_minutes": 20,
                "preparation_minutes": 10,
                "servings": 3,
                "instructions": (
                    "1. Clean and devein fresh prawns, leaving tails intact; toss with turmeric and salt.\n"
                    "2. Sauté fenugreek seeds, sliced onions, garlic, and curry leaves in hot coconut oil until fragrant.\n"
                    "3. Add roasted Jaffna curry powder and chili powder, stirring briefly on low heat.\n"
                    "4. Pour in thin coconut milk and tamarind water; bring to a simmer.\n"
                    "5. Add prawns and cook for just 4-5 minutes until curled and pink.\n"
                    "6. Stir in thick coconut milk, turn off heat, and let rest covered for 5 minutes."
                )
            },
            nutr_dict={"calories": 310.0, "protein": 28.0, "carbs": 8.0, "fat": 18.0, "fiber": 2.0, "sodium": 420.0},
            ingredients_list=[
                ("fresh prawns", "prawns", 350.0, "g"),
                ("coconut milk", "coconut milk", 1.0, "cup"),
                ("jaffna curry powder", "curry powder", 1.5, "tbsp"),
                ("tamarind paste", "tamarind", 1.0, "tsp"),
                ("fenugreek seeds", "fenugreek", 0.5, "tsp"),
                ("shallots", "shallots", 4.0, "pieces"),
                ("curry leaves", "curry leaves", 1.0, "sprig")
            ],
            allergen_keys=["shellfish"]
        )

        # 14. Sri Lankan Milk Rice (Kiribath) with Lunu Miris - Festive Breakfast
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Milk Rice (Kiribath) with Lunu Miris",
                "description": "Auspicious festive staple of white short-grain rice cooked to a soft pudding consistency in thick coconut milk, cut into diamond cakes.",
                "meal_type": "Breakfast",
                "cooking_minutes": 30,
                "preparation_minutes": 5,
                "servings": 4,
                "instructions": (
                    "1. Cook white raw rice in water in a heavy pot until soft and completely cooked.\n"
                    "2. Whisk thick coconut milk with 1 tsp salt until smooth.\n"
                    "3. Pour salted coconut milk into the hot rice; stir continuously on low heat until creamy and thick.\n"
                    "4. Transfer hot rice mixture onto a flat plate or banana leaf; smooth flat with a spatula to 1-inch thickness.\n"
                    "5. Allow to cool for 10 minutes, then slice into traditional diamond shapes.\n"
                    "6. Prepare Lunu Miris by crushing chili flakes, red onions, salt, and lime in a mortar and pestle; serve alongside."
                )
            },
            nutr_dict={"calories": 320.0, "protein": 5.0, "carbs": 52.0, "fat": 11.0, "fiber": 2.0, "sodium": 240.0},
            ingredients_list=[
                ("white raw rice", "rice", 2.0, "cups"),
                ("thick coconut milk", "coconut milk", 1.25, "cups"),
                ("water", "water", 3.5, "cups"),
                ("shallots", "shallots", 6.0, "pieces"),
                ("chili flakes", "chili powder", 1.5, "tbsp"),
                ("fresh lime juice", "lime", 1.0, "tbsp"),
                ("salt", "salt", 1.0, "tsp")
            ]
        )

        # 15. Sri Lankan String Hoppers (Idiyappam) - Naturally Gluten-Free, Vegan
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan String Hoppers (Idiyappam)",
                "description": "Delicate steamed rice flour vermicelli nests squeezed onto wicker mats and steamed; served with golden Kiri Hodi (coconut gravy).",
                "meal_type": "Breakfast",
                "cooking_minutes": 15,
                "preparation_minutes": 15,
                "servings": 4,
                "instructions": (
                    "1. Sift roasted rice flour into a bowl with salt.\n"
                    "2. Gradually add boiling hot water while stirring with a wooden spoon until a smooth, non-sticky dough forms.\n"
                    "3. Fill dough into an Idiyappam press fitted with fine vermicelli nozzles.\n"
                    "4. Squeeze in circular motions onto woven string hopper mats.\n"
                    "5. Steam in a tiered steamer for 8-10 minutes until soft and springy.\n"
                    "6. Stack nests on a platter and serve with fragrant turmeric coconut gravy (Kiri Hodi) and Pol Sambol."
                )
            },
            nutr_dict={"calories": 200.0, "protein": 4.0, "carbs": 44.0, "fat": 1.0, "fiber": 2.0, "sodium": 90.0},
            ingredients_list=[
                ("roasted rice flour", "rice flour", 2.0, "cups"),
                ("boiling water", "water", 1.5, "cups"),
                ("salt", "salt", 0.5, "tsp"),
                ("coconut milk", "coconut milk", 0.5, "cup")
            ]
        )

        # 16. Spicy Tempered Potatoes (Ala Theldala) - Vegan, Gluten-Free
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Spicy Tempered Potatoes (Ala Theldala)",
                "description": "Tender boiled potato cubes dry-fried in coconut oil with crushed Ceylon chili flakes, sweet sliced shallots, and fragrant curry leaves.",
                "meal_type": "Lunch",
                "cooking_minutes": 15,
                "preparation_minutes": 10,
                "servings": 3,
                "instructions": (
                    "1. Boil potatoes in salted water until just tender; peel and cut into 1-inch bite-sized cubes.\n"
                    "2. Heat coconut oil in a wide frying pan. Add mustard seeds and allow them to crackle.\n"
                    "3. Add sliced onions, green chilies, curry leaves, and minced garlic; sauté until golden.\n"
                    "4. Toss in crushed red chili flakes, turmeric powder, and salt.\n"
                    "5. Add the boiled potato cubes and gently toss on medium heat for 5 minutes until crispy red-spiced crust forms on the edges."
                )
            },
            nutr_dict={"calories": 180.0, "protein": 3.5, "carbs": 30.0, "fat": 6.0, "fiber": 3.5, "sodium": 220.0},
            ingredients_list=[
                ("potatoes", "potato", 400.0, "g"),
                ("red chili flakes", "chili powder", 1.0, "tbsp"),
                ("shallots", "shallots", 4.0, "pieces"),
                ("coconut oil", "oil", 1.5, "tbsp"),
                ("mustard seeds", "mustard seeds", 0.5, "tsp"),
                ("curry leaves", "curry leaves", 1.0, "sprig"),
                ("salt", "salt", 0.5, "tsp")
            ]
        )

        # 17. Crunchy Dhal Fritters (Parippu Vada / Masala Vadai) - Vegan, Gluten-Free
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Dhal Fritters (Parippu Vada / Masala Vadai)",
                "description": "Crispy golden tea-time savory patties made from coarse ground chana lentils, fennel seeds, fresh curry leaves, and spicy red chilies.",
                "meal_type": "Snack",
                "cooking_minutes": 15,
                "preparation_minutes": 20,
                "servings": 4,
                "instructions": (
                    "1. Soak chana dhal or toor dhal in water for 2 hours; reserve 2 tablespoons of whole lentils.\n"
                    "2. Coarsely pulse the remaining lentils in a food processor without adding any water.\n"
                    "3. Transfer to a bowl; fold in reserved whole lentils, chopped shallots, green chilies, curry leaves, fennel seeds, and salt.\n"
                    "4. Shape mixture into small round, flat discs using your hands.\n"
                    "5. Deep fry in hot coconut oil on medium heat for 4-5 minutes until deeply crunchy and amber brown.\n"
                    "6. Drain on paper towels and enjoy with hot Ceylon tea."
                )
            },
            nutr_dict={"calories": 170.0, "protein": 7.0, "carbs": 21.0, "fat": 7.0, "fiber": 5.0, "sodium": 180.0},
            ingredients_list=[
                ("chana dhal lentils", "lentils", 1.0, "cup"),
                ("fennel seeds", "fennel", 0.5, "tsp"),
                ("shallots", "shallots", 4.0, "pieces"),
                ("curry leaves", "curry leaves", 2.0, "sprigs"),
                ("green chili", "chili", 2.0, "pieces"),
                ("salt", "salt", 0.5, "tsp")
            ]
        )

        # 18. Jaffna Crab Curry (Kakuluwo Curry) - Contains Shellfish
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Jaffna Crab Curry (Kakuluwo Curry)",
                "description": "Celebrated coastal delicacy of blue swimming crabs simmered in fiery northern roasted spices, drumstick leaves (Murunga), and rich coconut milk.",
                "meal_type": "Dinner",
                "cooking_minutes": 35,
                "preparation_minutes": 15,
                "servings": 3,
                "instructions": (
                    "1. Clean crabs thoroughly, crack the large claws gently with a pestle, and drain.\n"
                    "2. Sauté fenugreek seeds, fennel seeds, sliced shallots, garlic, and ginger in coconut oil.\n"
                    "3. Add Jaffna roasted curry powder, coriander powder, and turmeric; stir for 1 minute on low heat.\n"
                    "4. Add thin coconut milk, tamarind juice, and crab pieces; bring to a vigorous boil.\n"
                    "5. Toss in fresh drumstick leaves (Murunga) and pour in thick coconut milk.\n"
                    "6. Simmer until crab shells turn brilliant crimson and gravy is aromatic, thick, and flavorful."
                )
            },
            nutr_dict={"calories": 290.0, "protein": 34.0, "carbs": 7.0, "fat": 14.0, "fiber": 2.0, "sodium": 460.0},
            ingredients_list=[
                ("fresh blue swimming crabs", "crab meat", 600.0, "g"),
                ("coconut milk", "coconut milk", 1.25, "cups"),
                ("jaffna roasted curry powder", "curry powder", 2.0, "tbsp"),
                ("drumstick leaves", "moringa leaves", 1.0, "cup"),
                ("tamarind pulp", "tamarind", 1.0, "tbsp"),
                ("shallots", "shallots", 6.0, "pieces"),
                ("garlic", "garlic", 4.0, "cloves")
            ],
            allergen_keys=["shellfish"]
        )

        # 19. Sri Lankan Black Pork Curry (Kalu Pol Mas) - Slow Cooked
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Black Pork Curry (Kalu Pol Mas)",
                "description": "Deeply spiced slow-cooked pork belly curry prepared with roasted desiccated coconut paste, black pepper, and Goraka souring agent.",
                "meal_type": "Dinner",
                "cooking_minutes": 45,
                "preparation_minutes": 15,
                "servings": 4,
                "instructions": (
                    "1. Dry roast grated coconut, uncooked rice, and coriander seeds in a skillet until dark brown (almost black) and grind into a fine paste.\n"
                    "2. Cut pork into 1-inch cubes and marinate with black pepper, Goraka paste, roasted curry powder, and salt.\n"
                    "3. Sauté shallots, ginger, garlic, lemongrass, and curry leaves in a clay pot.\n"
                    "4. Add marinated pork and brown the meat over medium flame for 8 minutes.\n"
                    "5. Stir in the roasted black coconut paste and 1 cup of water.\n"
                    "6. Simmer on low heat for 35 minutes until the meat is melt-in-the-mouth tender and coated in a glossy black gravy."
                )
            },
            nutr_dict={"calories": 440.0, "protein": 30.0, "carbs": 6.0, "fat": 32.0, "fiber": 2.0, "sodium": 410.0},
            ingredients_list=[
                ("pork cubes", "pork", 500.0, "g"),
                ("grated coconut", "coconut", 0.5, "cup"),
                ("black pepper", "black pepper", 1.5, "tbsp"),
                ("goraka paste", "goraka", 2.0, "tbsp"),
                ("lemongrass", "lemongrass", 1.0, "stalk"),
                ("garlic", "garlic", 3.0, "cloves"),
                ("curry leaves", "curry leaves", 1.0, "sprig")
            ]
        )

        # 20. Sri Lankan Vegetable Fried Rice - Contains Soy & Sesame
        add_full_recipe(
            r_dict={
                "title": "Sri Lankan Vegetable Fried Rice",
                "description": "Fragrant steamed basmati rice wok-tossed with crisp shredded cabbage, carrots, sweet leeks, garlic, ginger, and light soy sauce.",
                "meal_type": "Dinner",
                "cooking_minutes": 15,
                "preparation_minutes": 10,
                "servings": 3,
                "instructions": (
                    "1. Cook basmati rice and let chill completely in the refrigerator to prevent sticking.\n"
                    "2. Heat sesame oil in a wok on high flame. Sauté minced garlic, ginger, and green chilies for 30 seconds.\n"
                    "3. Toss in shredded cabbage, julienned carrots, and sliced leeks; stir-fry rapidly for 2 minutes keeping veggies crisp.\n"
                    "4. Add chilled basmati rice, light soy sauce, white pepper, and salt.\n"
                    "5. Toss vigorously on high heat for 3 minutes until steam rises and grains are separate and fragrant.\n"
                    "6. Serve with chili paste or vegetable Manchurian."
                )
            },
            nutr_dict={"calories": 310.0, "protein": 6.0, "carbs": 58.0, "fat": 6.0, "fiber": 3.0, "sodium": 490.0},
            ingredients_list=[
                ("basmati rice", "rice", 2.0, "cups"),
                ("shredded cabbage", "cabbage", 1.0, "cup"),
                ("julienned carrots", "carrots", 0.5, "cup"),
                ("sliced leeks", "leeks", 0.5, "cup"),
                ("soy sauce", "soy sauce", 1.5, "tbsp"),
                ("sesame oil", "sesame oil", 1.0, "tbsp"),
                ("garlic", "garlic", 2.0, "cloves"),
                ("ginger", "ginger", 1.0, "inch")
            ],
            allergen_keys=["soy", "sesame"]
        )

        # ==============================================================================
        # 5. Seed Curated Nutrition Tips & Food Safety News
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

        db.commit()
        db.close()
        print("Database seeding completed successfully! Seeded 20 authentic Sri Lankan recipes & nutrition tips.")

    except Exception as e:
        db.rollback()
        db.close()
        print(f"Error seeding database: {e}")
        raise e


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    seed_database(force=force_flag)

# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-a2a2e4ce323d"

SAMPLE_RECIPES = [
    {
        "id": "lemon-herb-grilled-chicken",
        "title": "Lemon Herb Grilled Chicken",
        "main_ingredients": ["chicken breast", "lemon", "garlic", "olive oil"],
        "ingredients": [
            "2 boneless, skinless chicken breasts",
            "1 lemon (juiced and zested)",
            "3 cloves garlic, minced",
            "2 tbsp olive oil",
            "1 tsp dried oregano",
            "Salt and black pepper to taste"
        ],
        "instructions": [
            "Whisk lemon juice, zest, minced garlic, olive oil, oregano, salt, and pepper in a bowl.",
            "Marinate chicken breasts for 15-20 minutes.",
            "Preheat skillet or grill pan over medium-high heat.",
            "Cook chicken for 6-7 minutes per side until internal temperature reaches 165°F (74°C).",
            "Let rest for 5 minutes before slicing. Serve with lemon wedges."
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "cuisine_style": "Mediterranean",
        "is_gluten_free": True,
        "is_dairy_free": True,
        "servings": 2
    },
    {
        "id": "creamy-tomato-basil-pasta",
        "title": "Quick Creamy Tomato Basil Pasta",
        "main_ingredients": ["pasta", "canned tomatoes", "garlic", "heavy cream"],
        "ingredients": [
            "8 oz penne or fettuccine pasta",
            "1 can (14 oz) crushed tomatoes",
            "3 cloves garlic, minced",
            "1/2 cup heavy cream (or coconut cream)",
            "1/4 cup grated parmesan cheese",
            "Fresh basil leaves, chopped",
            "1 tbsp olive oil",
            "Salt and red pepper flakes"
        ],
        "instructions": [
            "Boil pasta in salted water according to package directions; reserve 1/2 cup pasta water.",
            "In a skillet, heat olive oil and sauté garlic until fragrant (about 1 minute).",
            "Add crushed tomatoes, salt, and a pinch of red pepper flakes; simmer for 8 minutes.",
            "Stir in heavy cream and parmesan until sauce is smooth and creamy.",
            "Toss cooked pasta into sauce with fresh basil, adding reserved pasta water if needed."
        ],
        "prep_time_minutes": 5,
        "cook_time_minutes": 15,
        "cuisine_style": "Italian",
        "is_gluten_free": False,
        "is_dairy_free": False,
        "servings": 3
    },
    {
        "id": "tofu-veggie-stir-fry",
        "title": "Crispy Tofu & Veggie Stir-Fry",
        "main_ingredients": ["tofu", "broccoli", "bell pepper", "tamari"],
        "ingredients": [
            "1 block (14 oz) extra firm tofu, pressed and cubed",
            "2 cups broccoli florets",
            "1 red bell pepper, sliced",
            "2 tbsp gluten-free tamari or soy sauce",
            "1 tbsp sesame oil",
            "1 tbsp cornstarch",
            "1 tsp fresh ginger, grated",
            "1 tbsp honey or maple syrup"
        ],
        "instructions": [
            "Toss cubed tofu with cornstarch and a pinch of salt.",
            "Heat sesame oil in a wok or large pan over medium-high; fry tofu until golden and crisp (8 mins). Remove tofu.",
            "Add broccoli and bell pepper to the pan; stir-fry for 4-5 minutes until crisp-tender.",
            "Whisk tamari, ginger, and maple syrup; pour over veggies.",
            "Return tofu to the pan and toss until sauce coats everything evenly."
        ],
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "cuisine_style": "Asian",
        "is_gluten_free": True,
        "is_dairy_free": True,
        "servings": 2
    },
    {
        "id": "black-bean-avocado-tacos",
        "title": "15-Minute Black Bean & Avocado Tacos",
        "main_ingredients": ["black beans", "corn tortillas", "avocado", "salsa"],
        "ingredients": [
            "1 can (15 oz) black beans, drained and rinsed",
            "6 small corn tortillas (gluten-free)",
            "1 ripe avocado, sliced",
            "1/2 cup salsa",
            "1/2 tsp ground cumin",
            "1/2 tsp chili powder",
            "Fresh cilantro and lime wedges"
        ],
        "instructions": [
            "Warm black beans in a skillet with cumin, chili powder, and 2 tbsp water for 5 minutes; lightly mash.",
            "Warm corn tortillas in a dry skillet until pliable.",
            "Spoon seasoned black beans into tortillas.",
            "Top with avocado slices, fresh salsa, cilantro, and a squeeze of fresh lime juice."
        ],
        "prep_time_minutes": 5,
        "cook_time_minutes": 10,
        "cuisine_style": "Mexican",
        "is_gluten_free": True,
        "is_dairy_free": True,
        "servings": 2
    }
]


def seed():
    print(f"Connecting to Firestore with project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection("recipes")

    for item in SAMPLE_RECIPES:
        doc_id = item["id"]
        doc_ref = collection.document(doc_id)
        doc_ref.set(item)
        print(f"Seeded recipe: {item['title']} (ID: {doc_id})")

    print(f"Successfully seeded {len(SAMPLE_RECIPES)} recipes into 'recipes' collection.")


if __name__ == "__main__":
    seed()

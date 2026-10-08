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

"""Firestore tools for managing recipes."""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-a2a2e4ce323d"

_db: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def search_recipes(
    main_ingredients: Optional[List[str]] = None,
    is_gluten_free: Optional[bool] = None,
    is_dairy_free: Optional[bool] = None,
    cuisine_style: Optional[str] = None,
    max_prep_or_cook_time_minutes: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Search for recipes in the catalog matching criteria like ingredients, dietary restrictions, and cuisine.

    Args:
        main_ingredients: Optional list of main ingredients to match (e.g. ['chicken', 'tofu', 'pasta']).
        is_gluten_free: If True, only returns gluten-free recipes.
        is_dairy_free: If True, only returns dairy-free recipes.
        cuisine_style: Optional style/flavor (e.g., 'Mediterranean', 'Italian', 'Asian', 'Mexican').
        max_prep_or_cook_time_minutes: Optional maximum total time (prep + cook) in minutes.

    Returns:
        A list of matching recipe dictionaries.
    """
    db = get_db()
    docs = db.collection("recipes").stream()
    results = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # Filter by gluten-free
        if is_gluten_free is not None and data.get("is_gluten_free") != is_gluten_free:
            continue

        # Filter by dairy-free
        if is_dairy_free is not None and data.get("is_dairy_free") != is_dairy_free:
            continue

        # Filter by cuisine style
        if cuisine_style:
            recipe_cuisine = str(data.get("cuisine_style", "")).lower()
            if cuisine_style.lower() not in recipe_cuisine:
                continue

        # Filter by total time
        if max_prep_or_cook_time_minutes is not None:
            total_time = data.get("prep_time_minutes", 0) + data.get("cook_time_minutes", 0)
            if total_time > max_prep_or_cook_time_minutes:
                continue

        # Filter/score by main ingredients match
        if main_ingredients:
            recipe_ingredients_str = " ".join(
                [str(i).lower() for i in data.get("main_ingredients", []) + data.get("ingredients", [])]
            )
            matched = any(ing.lower() in recipe_ingredients_str for ing in main_ingredients)
            if not matched:
                continue

        results.append(data)

    return results


def get_recipe_details(recipe_id: str) -> Dict[str, Any]:
    """Retrieve full details for a specific recipe by ID.

    Args:
        recipe_id: The document ID of the recipe (e.g. 'lemon-herb-grilled-chicken').

    Returns:
        The recipe dictionary or an error message if not found.
    """
    db = get_db()
    doc_ref = db.collection("recipes").document(recipe_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Recipe with ID '{recipe_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_recipe(
    recipe_id: str,
    title: str,
    main_ingredients: List[str],
    ingredients: List[str],
    instructions: List[str],
    prep_time_minutes: int,
    cook_time_minutes: int,
    cuisine_style: str,
    is_gluten_free: bool = False,
    is_dairy_free: bool = False,
    servings: int = 2,
) -> Dict[str, Any]:
    """Save or update a recipe in the Firestore recipe catalog.

    Args:
        recipe_id: Unique slug/identifier for the recipe (e.g., 'sheet-pan-salmon').
        title: Title of the dish.
        main_ingredients: Primary key ingredients available or featured.
        ingredients: Full list of ingredients with quantities.
        instructions: Step-by-step cooking directions.
        prep_time_minutes: Time required for preparation in minutes.
        cook_time_minutes: Cooking time in minutes.
        cuisine_style: Style or flavor profile (e.g., 'Mediterranean', 'Mexican', 'Italian').
        is_gluten_free: Whether this dish is gluten-free.
        is_dairy_free: Whether this dish is dairy-free.
        servings: Number of servings.

    Returns:
        Status dictionary confirming the save.
    """
    db = get_db()
    doc_data = {
        "id": recipe_id,
        "title": title,
        "main_ingredients": main_ingredients,
        "ingredients": ingredients,
        "instructions": instructions,
        "prep_time_minutes": prep_time_minutes,
        "cook_time_minutes": cook_time_minutes,
        "cuisine_style": cuisine_style,
        "is_gluten_free": is_gluten_free,
        "is_dairy_free": is_dairy_free,
        "servings": servings,
    }
    db.collection("recipes").document(recipe_id).set(doc_data)
    return {"status": "success", "message": f"Recipe '{title}' saved with ID '{recipe_id}'.", "recipe": doc_data}


def generate_shopping_list(
    recipe_id: str,
    pantry_items_on_hand: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Generate a shopping checklist for a recipe by comparing needed ingredients against items already on hand.

    Args:
        recipe_id: Document ID of the recipe (e.g. 'lemon-herb-grilled-chicken').
        pantry_items_on_hand: Optional list of ingredients the user already has (e.g. ['olive oil', 'salt', 'garlic']).

    Returns:
        A dictionary containing the recipe title, ingredients on hand, and missing items categorized for shopping.
    """
    recipe = get_recipe_details(recipe_id)
    if "error" in recipe:
        return recipe

    on_hand = [item.strip().lower() for item in (pantry_items_on_hand or []) if item.strip()]
    all_ingredients = recipe.get("ingredients", [])

    have_items = []
    missing_items = []

    for ing in all_ingredients:
        ing_lower = ing.lower()
        # Check if any on-hand item is mentioned in this ingredient line
        if any(item in ing_lower for item in on_hand):
            have_items.append(ing)
        else:
            missing_items.append(ing)

    return {
        "recipe_id": recipe_id,
        "recipe_title": recipe.get("title"),
        "total_ingredients_count": len(all_ingredients),
        "items_on_hand": have_items,
        "shopping_list_needed": missing_items,
        "is_ready_to_cook": len(missing_items) == 0,
    }


def search_public_recipes(query: str) -> List[Dict[str, Any]]:
    """Search for real recipes online via the free public TheMealDB API.

    Args:
        query: Search term for dish or main ingredient (e.g. 'chicken', 'pasta', 'beef', 'salad').

    Returns:
        A list of recipes with meal name, category, cuisine area, instructions, and preview image URL.
    """
    import os
    import urllib.parse
    import urllib.request
    import json

    # Free test tier uses "1"; can override with THEMEALDB_API_KEY environment variable if provided
    api_key = os.getenv("THEMEALDB_API_KEY", "1")
    safe_query = urllib.parse.quote(query.strip())
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={safe_query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PantryChefAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            meals = payload.get("meals") or []
            
            results = []
            for m in meals[:5]:  # limit to top 5 results
                # Collect ingredients and measures
                ingredients = []
                for i in range(1, 21):
                    ing = (m.get(f"strIngredient{i}") or "").strip()
                    measure = (m.get(f"strMeasure{i}") or "").strip()
                    if ing:
                        ingredients.append(f"{measure} {ing}".strip())

                results.append({
                    "title": m.get("strMeal"),
                    "category": m.get("strCategory"),
                    "cuisine_style": m.get("strArea"),
                    "instructions": (m.get("strInstructions") or "").strip(),
                    "thumbnail_url": m.get("strMealThumb"),
                    "ingredients": ingredients,
                })
            return results
    except Exception as e:
        return [{"error": f"Failed to fetch public recipes: {str(e)}"}]


BUCKET_NAME = "pantry-chef-dishes-3743"


async def generate_dish_image(
    recipe_title: str,
    tool_context: Any,
    visual_description: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a photo of a plated dish using Gemini Imagen and save it to artifacts and Cloud Storage.

    Args:
        recipe_title: The name of the dish to visualize (e.g., 'Lemon Herb Grilled Chicken').
        tool_context: Injected ToolContext for saving session artifacts.
        visual_description: Optional additional styling cues (e.g. 'garnished with fresh herbs on a rustic ceramic plate').

    Returns:
        A dictionary with the public image URL and status.
    """
    import re
    import time
    from google import genai
    from google.genai import types
    from google.cloud import storage

    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    prompt = (
        f"Professional food photography of {recipe_title}. "
        f"{visual_description or 'Appetizing plating, natural soft lighting, high resolution, 4k, delicious weeknight dinner.'}"
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break
        if image_bytes:
            break

    if not image_bytes:
        return {"error": f"Failed to generate image for '{recipe_title}'."}

    # Clean slug for filename
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", recipe_title.lower()).strip("_")
    filename = f"{slug}_{int(time.time())}.jpg"

    # 1. Save with tool_context.save_artifact so it appears in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename, artifact_part)

    # 2. Upload the same image bytes to the public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "recipe_title": recipe_title,
        "artifact_filename": filename,
        "image_url": public_url,
        "message": f"Generated image for '{recipe_title}'. Public URL: {public_url}",
    }




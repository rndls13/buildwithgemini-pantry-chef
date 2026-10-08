# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.recipe_tools import (
    generate_dish_image,
    generate_shopping_list,
    get_recipe_details,
    save_recipe,
    search_public_recipes,
    search_recipes,
)

MODEL = "gemini-3.8-flash"


try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog

    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )
    instruction = schema_manager.generate_system_prompt(
        role_description=(
            "You are PantryChef, a weeknight dinner planner assistant. "
            "You help users plan quick dinners based on ingredients they have in their fridge or pantry, "
            "taking into account dietary restrictions (like gluten-free or dairy-free) and preferred cuisine styles. "
            "Use the recipe tools to search the internal catalog or public recipes (TheMealDB), fetch recipe details, "
            "compare pantry items to generate shopping lists, generate appetizing dish photos with generate_dish_image, "
            "and save new user-customized recipes."
        ),
        workflow_description="Analyze the request and return structured UI when appropriate.",
        ui_description=(
            "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
            "Never nest a Card inside a Card. "
            "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
            "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
            "nothing in adk web). "
            "You may include one Image component, but only when you have a public https "
            "URL for the image (for example the URL an image tool returns after uploading "
            "to a public bucket). Set the Image url to that exact https link, for example "
            '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
            "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
            "not have a public URL, add a short Text line noting the image instead. "
            "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
            "headings and emphasis. "
            "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
            "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
        ),
        include_schema=True,
        include_examples=True,
    )
except ImportError:
    from app.a2ui_prompt import INSTRUCTION as instruction


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        search_recipes,
        get_recipe_details,
        save_recipe,
        generate_shopping_list,
        search_public_recipes,
        generate_dish_image,
    ],
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)


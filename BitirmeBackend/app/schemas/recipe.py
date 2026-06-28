"""Recipe schemas.

``RecipeOut`` exposes every column of the ``recipes`` table (used as the AI
candidate pool). ``RecipeCreate`` / ``RecipeUpdate`` are used by the management
CRUD endpoints.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class RecipeBase(BaseModel):
    category: Optional[str] = None

    ilkbahar: Optional[int] = None
    yaz: Optional[int] = None
    sonbahar: Optional[int] = None
    kis: Optional[int] = None

    maliyet_norm: Optional[float] = None

    diabetes: Optional[int] = None
    celiac: Optional[int] = None
    lactose_intolerance: Optional[int] = None
    hypertension: Optional[int] = None
    pregnancy: Optional[int] = None
    obesity: Optional[int] = None
    cardiovascular_disease: Optional[int] = None
    kidney_disease: Optional[int] = None
    liver_disease: Optional[int] = None
    anemia: Optional[int] = None

    calories_pp: Optional[float] = None
    protein_g_pp: Optional[float] = None
    fat_g_pp: Optional[float] = None
    carbs_g_pp: Optional[float] = None
    fiber_g_pp: Optional[float] = None
    sugar_g_pp: Optional[float] = None
    sodium_mg_pp: Optional[float] = None
    calcium_mg_pp: Optional[float] = None
    iron_mg_pp: Optional[float] = None
    potassium_mg_pp: Optional[float] = None

    calories_pp_norm99: Optional[float] = None
    protein_g_pp_norm99: Optional[float] = None
    fat_g_pp_norm99: Optional[float] = None
    carbs_g_pp_norm99: Optional[float] = None
    fiber_g_pp_norm99: Optional[float] = None
    sugar_g_pp_norm99: Optional[float] = None
    sodium_mg_pp_norm99: Optional[float] = None
    calcium_mg_pp_norm99: Optional[float] = None
    iron_mg_pp_norm99: Optional[float] = None
    potassium_mg_pp_norm99: Optional[float] = None


class RecipeOut(RecipeBase):
    model_config = ConfigDict(from_attributes=True)

    recipe_id: int


class RecipeCreate(RecipeBase):
    recipe_id: Optional[int] = None


class RecipeUpdate(RecipeBase):
    pass

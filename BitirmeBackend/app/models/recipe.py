"""Recipe model.

Maps exactly to the existing ``recipes`` table used as the candidate pool for
the AI weekly-plan generator. The backend only reads from this table for plan
generation; CRUD endpoints are also provided for management.

Flag-like columns (season + health conditions) are stored as integers (0/1) to
stay compatible whether the underlying column is ``integer`` or ``boolean`` in
PostgreSQL.
"""
from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    recipe_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)

    # Seasonality flags
    ilkbahar: Mapped[int | None] = mapped_column(Integer, nullable=True)  # spring
    yaz: Mapped[int | None] = mapped_column(Integer, nullable=True)       # summer
    sonbahar: Mapped[int | None] = mapped_column(Integer, nullable=True)  # autumn
    kis: Mapped[int | None] = mapped_column(Integer, nullable=True)       # winter

    # Cost
    maliyet_norm: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Health-condition suitability flags
    diabetes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    celiac: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lactose_intolerance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hypertension: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pregnancy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    obesity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cardiovascular_disease: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kidney_disease: Mapped[int | None] = mapped_column(Integer, nullable=True)
    liver_disease: Mapped[int | None] = mapped_column(Integer, nullable=True)
    anemia: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Nutrition per person
    calories_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_g_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_g_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    fiber_g_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    sugar_g_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    sodium_mg_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    calcium_mg_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    iron_mg_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
    potassium_mg_pp: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Normalised (0-99) nutrition values for the AI model
    calories_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_g_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_g_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    fiber_g_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    sugar_g_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    sodium_mg_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    calcium_mg_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    iron_mg_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)
    potassium_mg_pp_norm99: Mapped[float | None] = mapped_column(Float, nullable=True)

"""FastAPI application entry point.

Run with:  uvicorn app.main:app --reload --port 3001
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine

# Import models so they are registered on the metadata before create_all.
from app import models  # noqa: F401
from app.routers import auth, meals, recipes, saved_recipes, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        # Only creates tables that don't exist yet. The existing "recipes"
        # table is left untouched.
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="NutriFlow Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All routes are served under /api to match the frontend's API base URL
# (REACT_APP_API_URL defaults to http://localhost:3001/api).
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(saved_recipes.router, prefix="/api")
app.include_router(meals.router, prefix="/api")


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}

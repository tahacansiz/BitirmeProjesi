-- ============================================================================
--  NutriFlow backend - helper schema (PostgreSQL, database: myapp)
-- ----------------------------------------------------------------------------
--  The "recipes" table is assumed to already exist (it is your AI candidate
--  pool). This file only defines the supporting tables the backend needs.
--  These are also created automatically on startup when AUTO_CREATE_TABLES=true.
-- ============================================================================

-- Basic accounts for the simple email/password login.
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name    VARCHAR(120),
    last_name     VARCHAR(120),
    is_onboarded  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Demographic / lifestyle / dietary preferences (exact schema as specified).
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id          INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    age              INTEGER,
    gender           VARCHAR(20),
    height_cm        DOUBLE PRECISION,
    weight_kg        DOUBLE PRECISION,
    activity_level   VARCHAR(20),
    weight_goal      VARCHAR(20),
    vegetarian       BOOLEAN NOT NULL DEFAULT FALSE,
    vegan            BOOLEAN NOT NULL DEFAULT FALSE,
    price_preference VARCHAR(20),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Favourite recipes per user.
CREATE TABLE IF NOT EXISTS saved_recipes (
    id        SERIAL PRIMARY KEY,
    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipe_id INTEGER NOT NULL,
    notes     TEXT,
    saved_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_saved_user_recipe UNIQUE (user_id, recipe_id)
);

-- Persisted generated weekly plans.
CREATE TABLE IF NOT EXISTS meal_plans (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start VARCHAR(20),
    plan       JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

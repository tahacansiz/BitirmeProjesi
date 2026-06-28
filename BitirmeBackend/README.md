# NutriFlow Backend

FastAPI + SQLAlchemy backend for the NutriFlow nutrition app (PostgreSQL,
database `myapp`). It serves the React frontend in the sibling `BitirmeAraYuz`
project and generates personalised weekly meal plans from the `recipes` table.

> **Auth note:** login is intentionally *basic* — no JWT and no authorization
> layer. Passwords are bcrypt-hashed; the login "token" is simply the user id,
> which the frontend returns in the `Authorization: Bearer <id>` header so the
> backend can identify the caller.

> **AI note:** the recommendation model is **not wired yet**. The weekly-plan
> generator in `app/services/ai_planner.py` is a deterministic placeholder that
> already filters recipes by season, budget, dietary preference and (optional)
> health condition. When the model is ready, send `build_model_payload()` to it
> and map the response into `WeeklyMealPlanOut`.

## Requirements

- Python 3.10+
- PostgreSQL with database `myapp` and an existing `recipes` table

## Setup

```bash
cd BitirmeBackend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                 # then edit DATABASE_URL credentials
```

Set your connection string in `.env`:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/myapp
```

The supporting tables (`users`, `user_profiles`, `saved_recipes`, `meal_plans`)
are created automatically on startup (`AUTO_CREATE_TABLES=true`). You can also
run `schema.sql` manually. The existing `recipes` table is never modified.

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
```

- API base: `http://localhost:3001/api`
- Health check: `http://localhost:3001/health`
- Interactive docs: `http://localhost:3001/docs`

The frontend's `REACT_APP_API_URL` defaults to `http://localhost:3001/api`, so
no extra config is needed for local development.

## Endpoints

| Method | Path                          | Description                              |
| ------ | ----------------------------- | ---------------------------------------- |
| POST   | `/api/auth/register`          | Create account                           |
| POST   | `/api/auth/login`             | Email/password login                     |
| POST   | `/api/auth/logout`            | No-op (client discards token)            |
| POST   | `/api/auth/refresh`           | No-op (tokens don't expire)              |
| GET    | `/api/users/profile`          | Current user + profile                   |
| PUT    | `/api/users/profile`          | Update profile                           |
| POST   | `/api/users/onboarding/complete` | Save profile + mark onboarded         |
| GET    | `/api/recipes`                | List recipes (filter: `category`, `season`) |
| GET    | `/api/recipes/search?q=`      | Search by category                       |
| GET    | `/api/recipes/{id}`           | Get one recipe                           |
| POST   | `/api/recipes`                | Create recipe                            |
| PUT    | `/api/recipes/{id}`           | Update recipe                            |
| DELETE | `/api/recipes/{id}`           | Delete recipe                            |
| GET    | `/api/saved-recipes`          | User's saved recipes                     |
| POST   | `/api/saved-recipes`          | Save a recipe (`{ "recipe_id": n }`)     |
| DELETE | `/api/saved-recipes/{id}`     | Remove a saved recipe                    |
| GET    | `/api/meals/weekly-plan`      | Generate 7-day plan (AI stub)            |
| POST   | `/api/meals/suggest`          | Fresh AI suggestion                      |
| GET    | `/api/meals/alternatives`     | Replacement meals (`category=`)          |
| POST   | `/api/meals/plan`             | Save a generated plan                    |
| GET    | `/api/meals/plan`             | Latest saved plan                        |

User-scoped endpoints require the `Authorization: Bearer <token>` header, where
`<token>` is the value returned by `/api/auth/login`.

## Schema mapping notes

- Frontend `UserProfile.height/weight` ↔ DB `height_cm/weight_kg`.
- `foodPreferences` is derived from the `vegetarian` / `vegan` booleans.
- `healthCondition` from the frontend is **not persisted** (the specified
  `user_profiles` schema has no column for it). It can still be passed as a
  query/body param to the meal endpoints to influence plan generation. Add a
  `health_condition` column if you want it stored.

## Project layout

```
app/
  main.py            App + router wiring
  deps.py            Auth/db dependencies
  core/              config, database, security
  models/            SQLAlchemy models (users, user_profiles, recipes, ...)
  schemas/           Pydantic request/response models
  routers/           auth, users, recipes, saved_recipes, meals
  services/
    ai_planner.py    Weekly-plan generator (placeholder for the AI model)
schema.sql           Reference DDL for the supporting tables
```

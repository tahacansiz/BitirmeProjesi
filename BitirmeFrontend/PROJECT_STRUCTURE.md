# Project Structure Detailed Guide

Complete explanation of every directory and file in the project.

## 📂 Complete Directory Tree

```
BitirmeAraYuz/
├── public/
│   └── index.html                 # HTML entry point for React
│
├── src/
│   ├── components/                # Reusable React components
│   │   ├── common/
│   │   │   ├── Button.tsx         # Customizable button component
│   │   │   ├── Input.tsx          # Form input with labels & validation
│   │   │   ├── Header.tsx         # Navigation header with user menu
│   │   │   ├── Alert.tsx          # Notification/alert messages
│   │   │   └── LoadingSpinner.tsx # Loading indicator animation
│   │   │
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx      # Email/password login form
│   │   │   └── OnboardingForm.tsx # Multi-section onboarding form
│   │   │
│   │   ├── dashboard/
│   │   │   └── MealSuggestionCard.tsx  # Meal suggestion card display
│   │   │
│   │   ├── recipe/
│   │   │   ├── RecipeCard.tsx     # Individual recipe card
│   │   │   └── RecipeGrid.tsx     # Grid layout for recipes
│   │   │
│   │   └── profile/
│   │       └── ProfileForm.tsx    # Editable user profile form
│   │
│   ├── pages/                     # Full page components
│   │   ├── Login.tsx              # Login page with redirects
│   │   ├── Onboarding.tsx         # Onboarding page (first-time only)
│   │   ├── Dashboard.tsx          # Main dashboard with meal plan
│   │   ├── Recipes.tsx            # Recipe browser & search
│   │   ├── SavedRecipes.tsx       # User's saved recipes
│   │   └── Profile.tsx            # User profile management
│   │
│   ├── layouts/                   # Layout wrapper components
│   │   ├── AuthLayout.tsx         # Layout for auth pages (centered)
│   │   └── AppLayout.tsx          # Main app layout (header+footer)
│   │
│   ├── context/
│   │   └── AuthContext.tsx        # Global auth state (user, login, logout)
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useAuth.ts             # Auth context hook & helpers
│   │   ├── useRecipes.ts          # Recipe fetching & management
│   │   └── useMeals.ts            # Meal suggestions & planning
│   │
│   ├── services/                  # Business logic & API communication
│   │   ├── api/
│   │   │   ├── client.ts          # HTTP client with auth handling
│   │   │   └── endpoints.ts       # Centralized API endpoint definitions
│   │   │
│   │   ├── auth/
│   │   │   └── authService.ts     # Authentication service (login, logout, onboarding)
│   │   │
│   │   └── recipe/
│   │       ├── recipeService.ts   # Recipe CRUD & search
│   │       └── mealService.ts     # Meal suggestions & planning
│   │
│   ├── types/                     # TypeScript type definitions
│   │   ├── auth.ts                # Auth types (User, Login, etc.)
│   │   ├── recipe.ts              # Recipe types
│   │   ├── meal.ts                # Meal types
│   │   └── index.ts               # Common types & exports
│   │
│   ├── mock/                      # Mock data for development
│   │   ├── recipes.ts             # 5 sample recipes with full data
│   │   ├── meals.ts               # Sample meal suggestions
│   │   └── users.ts               # Sample users & auth helper
│   │
│   ├── styles/                    # CSS styling
│   │   ├── globals.css            # Theme variables, resets, base styles
│   │   ├── components.css         # All component styles
│   │   ├── layouts.css            # Layout styles
│   │   └── pages.css              # Page-specific styles
│   │
│   ├── App.tsx                    # Main app component with routing
│   └── index.tsx                  # React app entry point
│
├── .env.example                   # Example environment variables
├── README.md                      # Project overview
├── ARCHITECTURE.md                # Architecture guide
├── API_INTEGRATION.md             # Backend integration guide
├── PROJECT_STRUCTURE.md           # This file
├── package.json                   # Dependencies and scripts
└── tsconfig.json                  # TypeScript configuration
```

## 📄 File Descriptions

### Public Files

#### `public/index.html`
- HTML entry point for React application
- Contains the `<div id="root">` where React mounts
- Meta tags for app info, viewport, theme color

### Source Files

#### `src/App.tsx`
- Main application component
- Sets up React Router with all routes
- Wraps app with AuthProvider context
- Imports all CSS files

Routes defined:
- `/login` - Login page
- `/onboarding` - Onboarding flow
- `/` & `/dashboard` - Main dashboard
- `/recipes` - Recipe browser
- `/saved-recipes` - Saved recipes
- `/profile` - User profile
- `*` - Catch-all redirect to login

#### `src/index.tsx`
- Application entry point
- Renders App component into DOM root
- Uses React.StrictMode for development

### Component Files (`src/components/`)

#### Common Components
Each common component is a reusable building block:

**Button.tsx**
- Props: variant (primary/secondary/danger/success), size (small/medium/large), fullWidth, isLoading
- Used throughout app for all interactive buttons
- Handles loading state automatically

**Input.tsx**
- Props: label, error, helpText, plus standard HTML input props
- Shows error messages below input
- Optional help text for guidance

**Header.tsx**
- Fixed at top of app layout
- Logo/branding on left
- Navigation links in center (dashboard, recipes, saved, profile)
- User menu on right with logout

**Alert.tsx**
- Props: type (success/error/warning/info), message, autoClose, onClose
- Animated slide-in
- Supports auto-dismiss

**LoadingSpinner.tsx**
- Props: size (small/medium/large), message
- Rotating spinner animation
- Optional loading message

#### Auth Components

**LoginForm.tsx**
- Email & password inputs with validation
- Pre-filled demo credentials for testing
- Shows auth errors from context
- Form validation before submission
- Links to onboarding after successful login

**OnboardingForm.tsx**
- Multi-section form (Personal, Lifestyle, Health)
- Collects: age, height, weight, gender, activity level, health conditions
- Input validation (age 13-120, height 100-250cm, weight 30-300kg)
- Calls authService.completeOnboarding() on submit
- Redirects to dashboard on success

#### Dashboard Components

**MealSuggestionCard.tsx**
- Displays meal suggestion with recipe image
- Shows reason for suggestion
- Displays calories and protein
- Optional onClick handler for more details

#### Recipe Components

**RecipeCard.tsx**
- Displays individual recipe in card format
- Shows: image, title, nutrition stats (cal, protein, carbs, fat)
- "Save" button that changes to "✓ Saved" when saved
- Difficulty badge (easy/medium/hard)
- Hover effects with image zoom

**RecipeGrid.tsx**
- Grid layout for multiple recipes
- Responsive: 4 columns desktop, 2 tablet, 1 mobile
- Accepts savedRecipeIds to show save status
- Empty state message when no recipes

#### Profile Components

**ProfileForm.tsx**
- Displays current user profile
- Toggle between view and edit modes
- Edit mode shows input fields
- Save changes calls authService.updateProfile()
- Shows success/error messages

### Page Files (`src/pages/`)

#### Login.tsx
- Simple wrapper around LoginForm
- Redirects to dashboard if already logged in
- Used within AuthLayout

#### Onboarding.tsx
- Shows OnboardingForm if user not onboarded
- Redirects to login if not authenticated
- Redirects to dashboard if already onboarded

#### Dashboard.tsx
- Welcome section with user greeting
- Today's meal plan (4 meal slots: breakfast, lunch, dinner, snack)
- Nutrition summary (calories, protein, carbs, fat)
- Suggested recipes section
- Quick action buttons

#### Recipes.tsx
- Search bar at top
- Recipe grid below
- Handles saving/removing recipes
- Shows loading spinner while fetching

#### SavedRecipes.tsx
- Displays user's saved recipes
- Can remove recipes
- Shows count of saved recipes
- Empty state if no recipes saved

#### Profile.tsx
- Wrapper around ProfileForm
- Ensures user is authenticated and onboarded
- Simple, single-purpose page

### Layout Files (`src/layouts/`)

#### AuthLayout.tsx
- Used for login and onboarding pages
- Gradient background (purple/indigo)
- Centered content box
- No header/navigation

#### AppLayout.tsx
- Main layout for logged-in pages
- Header at top with navigation
- Main content area
- Footer at bottom
- Used with ProtectedRoute in routing

### Context Files (`src/context/`)

#### AuthContext.tsx
- Provides global auth state
- Context type: AuthContextType
- State: user, isLoading, error
- Methods: login(), logout(), clearError()
- Initializes from localStorage on mount

### Hook Files (`src/hooks/`)

#### useAuth.ts
- `useAuth()` - Full auth context access
- `useAuthStatus()` - Just isAuthenticated, isLoading, user
- `useOnboarding()` - Check isOnboarded and needsOnboarding

#### useRecipes.ts
- `useRecipes()` - Fetch all recipes, search
- `useSavedRecipes()` - Fetch saved, save, remove

#### useMeals.ts
- `useMealSuggestions()` - Get meal suggestions
- `useMealPlan()` - Get plan for specific date

### Service Files (`src/services/`)

#### API Client (`api/client.ts`)
- HTTP client with methods: get, post, put, delete
- Adds auth token to all requests
- Central error handling
- Mock implementation, ready for real API

#### API Endpoints (`api/endpoints.ts`)
- Centralized endpoint definitions
- Easy to update all endpoints in one place
- Organized by resource

#### Auth Service (`auth/authService.ts`)
- `login()` - Authenticate user
- `logout()` - Clear session
- `getCurrentUser()` - Get user from localStorage
- `isAuthenticated()` - Check token exists
- `isOnboarded()` - Check profile exists
- `completeOnboarding()` - Mark onboarded + save profile
- `updateProfile()` - Update user profile

#### Recipe Service (`recipe/recipeService.ts`)
- `getRecipes()` - All recipes
- `getRecipeById()` - Single recipe
- `searchRecipes()` - Search by query
- `filterRecipes()` - Filter by criteria
- `getSavedRecipes()` - User's saved
- `saveRecipe()` - Add to saved
- `removeSavedRecipe()` - Remove from saved

#### Meal Service (`recipe/mealService.ts`)
- `getMealSuggestions()` - AI suggestions
- `getMealPlan()` - Plan for date
- `saveMealPlan()` - Save plan
- `suggestForMealType()` - Suggestions for specific meal

### Type Files (`src/types/`)

#### auth.ts
- `LoginCredentials` - email, password
- `LoginResponse` - success, user, token, message
- `AuthContextType` - context shape
- `User` - id, email, firstName, isOnboarded, profile
- `UserProfile` - age, height, weight, gender, activityLevel, healthCondition

#### recipe.ts
- `Recipe` - full recipe object
- `Ingredient` - ingredient details
- `SavedRecipe` - recipe + savedAt
- `RecipeFilter` - filter options

#### meal.ts
- `MealSuggestion` - recipe + reason
- `MealPlan` - date + meals + totals

#### index.ts
- `ApiResponse<T>` - Generic API response wrapper
- `PaginatedResponse<T>` - Paginated results

### Mock Files (`src/mock/`)

#### recipes.ts
- Array of 5 complete recipes with:
  - Full metadata (title, description, difficulty, prep/cook time)
  - Nutrition info (calories, protein, carbs, fat)
  - Ingredients with measurements
  - Step-by-step instructions
  - Tags for filtering

#### meals.ts
- Array of meal suggestions with:
  - Recipe reference
  - Reason for suggestion
  - Nutrition summary

#### users.ts
- Sample users for testing
- `mockAuthResponse()` - Simulates login
- `simulateApiDelay()` - Adds realistic latency

### Style Files (`src/styles/`)

#### globals.css
- CSS variables (colors, spacing, fonts, shadows, etc.)
- Global resets and base styles
- Typography defaults
- Utility classes

#### components.css
- Styles for all components:
  - Buttons (4 variants × 3 sizes)
  - Inputs (with error states)
  - Header (logo, nav, user menu)
  - Loading spinner
  - Alerts (4 types)
  - Recipe cards and grid
  - Meal suggestion cards

#### layouts.css
- AuthLayout - centered gradient
- AppLayout - header, main, footer

#### pages.css
- Login page styles
- Onboarding page styles
- Dashboard page styles
- Recipes page styles
- Saved recipes page styles
- Profile page styles

## 🔄 Import Patterns

### Component Imports
```typescript
import { RecipeCard } from '../components/recipe/RecipeCard';
import { Button } from '../components/common/Button';
```

### Type Imports
```typescript
import type { Recipe, RecipeFilter } from '../types/recipe';
import { User } from '../types/auth';
```

### Service Imports
```typescript
import { authService } from '../services/auth/authService';
import { recipeService } from '../services/recipe/recipeService';
```

### Hook Imports
```typescript
import { useAuth } from '../hooks/useAuth';
import { useRecipes } from '../hooks/useRecipes';
```

## 📊 File Statistics

- **Total Components**: 13
- **Total Pages**: 6
- **Total Services**: 3
- **Total Custom Hooks**: 6
- **Total Type Files**: 4
- **Total Mock Files**: 3
- **Total Style Files**: 4
- **Lines of Code**: ~3,500+

## 🎯 Key Principles

1. **Single Responsibility** - Each file has one job
2. **Co-location** - Related files grouped together
3. **Clear Dependencies** - Services → Hooks → Components
4. **Type Safety** - All code TypeScript
5. **DRY (Don't Repeat Yourself)** - Reusable components
6. **Easy to Extend** - Clear patterns to follow

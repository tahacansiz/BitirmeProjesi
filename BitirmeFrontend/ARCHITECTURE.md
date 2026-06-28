# Architecture Guide

This document explains the architecture decisions and how different parts of the application work together.

## 🏗️ Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────┐
│     UI Layer (Components)           │  - React components
│  (Pages, Layouts, Reusable)         │  - User interactions
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    State Management Layer           │  - React Context
│  (Context, Custom Hooks)            │  - Global state
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Business Logic Layer             │  - Services
│  (Services, Hooks)                  │  - Data transformation
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Data Access Layer                │  - API Client
│  (API Client, Endpoints)            │  - Mock Data
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    External Services                │  - Backend API
│  (REST, GraphQL, etc.)              │  - Real data
└─────────────────────────────────────┘
```

## 📂 Directory Structure & Responsibilities

### `/src/components` - React Components
Presentation logic only. No direct API calls.

#### Subcategories:
- **common/** - Generic, reusable components used across the app
  - `Button.tsx` - Customizable button with variants
  - `Input.tsx` - Form input with validation display
  - `Header.tsx` - Navigation header
  - `Alert.tsx` - Notification component
  - `LoadingSpinner.tsx` - Loading indicator

- **auth/** - Authentication-related components
  - `LoginForm.tsx` - Login form with validation
  - `OnboardingForm.tsx` - Multi-section onboarding form

- **dashboard/** - Dashboard-specific components
  - `MealSuggestionCard.tsx` - Card displaying meal suggestions

- **recipe/** - Recipe-related components
  - `RecipeCard.tsx` - Individual recipe display
  - `RecipeGrid.tsx` - Grid layout for recipes

- **profile/** - Profile management
  - `ProfileForm.tsx` - Editable profile form

### `/src/pages` - Page Components
Full-page components that handle navigation and layout.

Each page:
- Checks authentication status
- Handles redirects
- Composes smaller components
- Manages page-level state (filters, search, etc.)

Pages:
- `Login.tsx` - Login page
- `Onboarding.tsx` - Onboarding page
- `Dashboard.tsx` - Main dashboard
- `Recipes.tsx` - Recipe browser
- `SavedRecipes.tsx` - Saved recipes collection
- `Profile.tsx` - User profile

### `/src/layouts` - Layout Components
Wrapper components for consistent structure.

- `AuthLayout.tsx` - Used for login/onboarding (centered, gradient background)
- `AppLayout.tsx` - Used for logged-in pages (header, footer, main content)

### `/src/context` - Global State Management
React Context for application-wide state.

- `AuthContext.tsx` - Manages:
  - Current user
  - Authentication status
  - Login/logout
  - Error messages

Future contexts could include:
- `RecipeContext.tsx` - Saved recipes
- `PreferencesContext.tsx` - User preferences
- `NotificationContext.tsx` - Toast notifications

### `/src/hooks` - Custom React Hooks
Reusable stateful logic.

**Auth Hooks:**
- `useAuth()` - Access auth context
- `useAuthStatus()` - Simplified auth status
- `useOnboarding()` - Check onboarding status

**Recipe Hooks:**
- `useRecipes()` - Fetch and manage recipes
- `useSavedRecipes()` - Manage saved recipes with CRUD operations

**Meal Hooks:**
- `useMealSuggestions()` - Get meal suggestions
- `useMealPlan()` - Get meal plan for specific date

### `/src/services` - Business Logic & API Integration
Service classes handle data fetching, transformation, and caching.

#### API Layer
- `api/client.ts` - HTTP client with auth handling
- `api/endpoints.ts` - Centralized endpoint definitions

#### Service Classes
- `auth/authService.ts` - Authentication logic
- `recipe/recipeService.ts` - Recipe management
- `recipe/mealService.ts` - Meal suggestions

### `/src/types` - TypeScript Definitions
Centralized type definitions for the entire app.

- `auth.ts` - User, auth response, login credentials
- `recipe.ts` - Recipe, ingredient, saved recipe
- `meal.ts` - Meal suggestion, meal plan
- `index.ts` - Common types (API response, pagination)

### `/src/mock` - Mock Data for Development
Realistic sample data simulating API responses.

- `recipes.ts` - 5 complete recipes with all properties
- `meals.ts` - Sample meal suggestions
- `users.ts` - Sample users and auth helper

### `/src/styles` - CSS Files
Organized by scope.

- `globals.css` - Theme variables, resets, base styles
- `components.css` - Component-level styles
- `layouts.css` - Layout styles
- `pages.css` - Page-specific styles

## 🔄 Data Flow Examples

### Example 1: User Login Flow

```
1. User enters credentials
   ↓
2. LoginForm calls auth.login()
   ↓
3. useAuth hook calls authService.login()
   ↓
4. authService calls mock authResponse (or API)
   ↓
5. Response stored in localStorage
   ↓
6. AuthContext updated with user data
   ↓
7. useAuthStatus hook notifies components
   ↓
8. Navigation redirects to appropriate page
```

### Example 2: Fetch Recipes

```
1. RecipesPage mounts
   ↓
2. useRecipes hook executes
   ↓
3. Hook calls recipeService.getRecipes()
   ↓
4. Service returns mock recipes (or API response)
   ↓
5. Hook state updated with recipes
   ↓
6. Component re-renders with data
   ↓
7. User interacts with recipe cards
```

### Example 3: Save Recipe

```
1. User clicks "Save Recipe" button
   ↓
2. RecipeCard calls onSave(recipeId)
   ↓
3. useSavedRecipes.saveRecipe() called
   ↓
4. Service updates mock data (or API call)
   ↓
5. UI state updated
   ↓
6. Button shows "Saved" state
```

## 🎯 Design Patterns Used

### 1. **Component Composition**
Large components are broken into smaller, reusable pieces.

```tsx
// Instead of:
<LoginForm user={user} onSubmit={...} />

// We have:
<LoginForm />  // Self-contained, manages own state
```

### 2. **Custom Hooks for Logic Extraction**
Business logic extracted from components into hooks.

```tsx
// In component:
const { recipes, isLoading, error } = useRecipes();

// In hook:
export const useRecipes = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  // ... logic here
};
```

### 3. **Service Layer Pattern**
Centralized business logic in service classes.

```tsx
// Component calls hook
// Hook calls service
// Service calls API or mock data
// Component doesn't know where data comes from
```

### 4. **Context API for Global State**
Avoid prop drilling by using Context for app-wide state.

```tsx
const { user, isAuthenticated } = useAuth();
// Available in any component without prop passing
```

### 5. **Type-First Development**
Types defined before implementation.

```typescript
// Types guide implementation
interface Recipe {
  id: string;
  title: string;
  calories: number;
  // ... other properties
}
```

## 🔌 Backend Integration Points

### Easy to Replace:

1. **API Client** (`src/services/api/client.ts`)
   - Replace mock implementation with real fetch/axios

2. **Service Methods** (e.g., `recipeService.getRecipes()`)
   - Change from mock data to API call

3. **Authentication** (`src/services/auth/authService.ts`)
   - Replace with real authentication service

4. **Storage** (currently localStorage)
   - Replace with cookies or session storage

## 📊 State Management

### Current: React Context + Hooks
- Simple for this project size
- No external dependencies
- Easy to understand

### Future Considerations:
- **Redux** - If state becomes complex
- **Zustand** - Lightweight alternative
- **Recoil** - Atomic state management

## 🚀 Performance Optimizations

### Implemented:
- Code splitting (lazy loading pages via routing)
- Memoization opportunities in components
- CSS variables for theme switching without re-render

### Future:
- React.memo for expensive components
- useMemo for expensive calculations
- useCallback for event handlers
- Image optimization with Next.js
- Caching strategies in service layer

## 🔐 Security Considerations

### Current Implementation:
- Token stored in localStorage (consider alternatives)
- No sensitive data in state
- Protected routes with redirects

### Future Improvements:
- HttpOnly cookies for tokens
- CSRF protection
- XSS prevention
- Rate limiting on API calls
- Input validation and sanitization

## 📝 Code Organization Best Practices

### File Naming
- Components: PascalCase (e.g., `RecipeCard.tsx`)
- Services: camelCase (e.g., `authService.ts`)
- Types: camelCase (e.g., `auth.ts`)
- Styles: kebab-case matching component (e.g., `.recipe-card`)

### Export Patterns
```typescript
// Named exports for reusable items
export const Button: React.FC<ButtonProps> = (...) => {}

// Single default export for pages
export default DashboardPage
```

### Folder Structure Rules
- Keep related files together
- One component per file (usually)
- Group by feature/domain
- Common utilities in /common

## 🎓 Learning Resources

For team members:
1. Read this guide first
2. Explore the existing code
3. Follow the established patterns
4. Check types before implementation
5. Use service layer for all data access

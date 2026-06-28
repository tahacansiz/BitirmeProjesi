# NutriFlow - Production-Ready Nutrition Frontend

A modern, scalable, and backend-ready React frontend for a nutrition web application with user authentication, onboarding, meal suggestions, and recipe management.

## 🚀 Key Features

✅ **Production-Ready Architecture** - Clean, scalable structure ready for enterprise deployment
✅ **Backend-Ready** - Designed for easy API integration
✅ **Authentication Flow** - Login with redirect to onboarding (first-time only)
✅ **Onboarding System** - Collect user health data (age, weight, height, etc.)
✅ **Dashboard** - Welcome section with personalized meal plans
✅ **Recipe Management** - Browse, search, and save recipes
✅ **Profile Management** - View and update user profile
✅ **Mock Data** - Fully functional with mock data for demonstration
✅ **TypeScript** - Full type safety across the app
✅ **Responsive Design** - Works on desktop, tablet, and mobile

## 📁 Project Structure

```
src/
├── components/              # Reusable React components
│   ├── common/             # Generic components (Button, Input, Header, etc.)
│   ├── auth/               # Authentication components (LoginForm, OnboardingForm)
│   ├── dashboard/          # Dashboard-specific components
│   ├── recipe/             # Recipe components (RecipeCard, RecipeGrid)
│   └── profile/            # Profile management components
├── pages/                  # Page components (full pages)
├── layouts/                # Layout wrappers (AuthLayout, AppLayout)
├── context/                # React Context (AuthContext for global state)
├── hooks/                  # Custom React hooks
├── services/               # Business logic & API communication
│   ├── api/               # HTTP client and endpoints
│   ├── auth/              # Authentication service
│   └── recipe/            # Recipe and meal services
├── types/                  # TypeScript type definitions
├── mock/                   # Mock data for development
├── styles/                 # CSS files
│   ├── globals.css        # Global styles and theme variables
│   ├── components.css     # Component styles
│   ├── layouts.css        # Layout styles
│   └── pages.css          # Page-specific styles
├── App.tsx                # Main app component with routing
└── index.tsx              # Application entry point
```

## 🔐 Authentication Flow

1. **Login Page** (`/login`)
   - User enters email and password
   - Demo credentials: `john@example.com` / `password123`
   - On success → Check onboarding status

2. **Onboarding Page** (`/onboarding`) - Only if user NOT onboarded
   - Collects: Age, Height, Weight, Gender, Activity Level, Health Conditions
   - Only appears once per user
   - On completion → Redirect to Dashboard

3. **Dashboard** (`/`)
   - Main hub of the application
   - Shows personalized greeting
   - Displays meal suggestions
   - Quick access to recipes and saved recipes

## 🎨 Demo Credentials

```
Email: john@example.com
Password: password123
```

## 🏗️ Architecture Principles

### 1. **Separation of Concerns**
- **Components**: UI and presentation logic only
- **Services**: Business logic and API communication
- **Context**: Global state management
- **Hooks**: Reusable stateful logic

### 2. **Backend-Ready Design**
- Service layer abstracts API calls
- Mock implementations can be easily replaced with real API calls
- Type definitions match API contracts
- API client with proper error handling

### 3. **Scalability**
- Component composition pattern
- Custom hooks for reusable logic
- Proper state management with Context API
- Easy to extend with new features

### 4. **Type Safety**
- Full TypeScript coverage
- Centralized type definitions
- Proper interface definitions for all data

## 🔄 Data Flow

```
User Interaction
    ↓
Component (UI Layer)
    ↓
Custom Hook (State Management)
    ↓
Service Layer (Business Logic)
    ↓
API Client (HTTP Communication)
    ↓
Backend API (or Mock Data)
```

## 📝 Services Overview

### AuthService
```typescript
- login(credentials)          // User authentication
- logout()                    // Logout user
- getCurrentUser()            // Get current user from localStorage
- isAuthenticated()           // Check auth status
- isOnboarded()              // Check onboarding status
- completeOnboarding(data)    // Mark onboarding complete
- updateProfile(updates)      // Update user profile
```

### RecipeService
```typescript
- getRecipes()               // Get all recipes
- getRecipeById(id)          // Get specific recipe
- searchRecipes(query)       // Search recipes
- filterRecipes(...)         // Filter by criteria
- getSavedRecipes()          // Get user's saved recipes
- saveRecipe(id)             // Save recipe for user
- removeSavedRecipe(id)      // Remove saved recipe
```

### MealService
```typescript
- getMealSuggestions()       // Get AI suggestions (mock data)
- getMealPlan(date)          // Get meal plan for specific date
- saveMealPlan(plan)         // Save meal plan
- suggestForMealType(type)   // Get suggestions for meal type
```

## 🎯 Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn
- React Router v6
- TypeScript

### Installation

```bash
# Install dependencies
npm install

# Or with yarn
yarn install

# Install React Router if not included
npm install react-router-dom
```

### Running the App

```bash
# Start development server
npm start

# Build for production
npm run build
```

## 🔌 Backend Integration Guide

See [API_INTEGRATION.md](./API_INTEGRATION.md) for detailed instructions on:
- Connecting to your backend
- Replacing mock data with API calls
- Authentication token handling
- Error handling best practices

## 📊 Type Definitions

All types are defined in `/src/types/`:
- `auth.ts` - Authentication types
- `recipe.ts` - Recipe and ingredient types
- `meal.ts` - Meal suggestion types
- `index.ts` - Centralized exports and common types

## 🎨 Styling System

- **CSS Variables** for consistent theming
- **Dark mode ready** - Can be easily extended
- **Responsive design** - Mobile-first approach
- **Component-scoped styles** - Easy to maintain

### Color Variables
```css
--color-primary: #6366f1 (Indigo)
--color-success: #10b981 (Green)
--color-error: #ef4444 (Red)
--color-warning: #f59e0b (Amber)
```

## 🧪 Mock Data

Mock data files provide realistic sample data:
- `mock/recipes.ts` - 5 sample recipes with full details
- `mock/meals.ts` - Sample meal suggestions
- `mock/users.ts` - Sample users and auth helper

All mock services include configurable delays to simulate API latency.

## 🚀 Deployment

### Frontend Deployment Options
1. **Vercel** - Recommended for Next.js/React
2. **Netlify** - Great for static deployments
3. **AWS S3 + CloudFront** - Enterprise option
4. **Docker** - For containerized deployments

### Environment Variables
```
REACT_APP_API_URL=https://api.example.com
REACT_APP_ENV=production
```

## 📈 Future Enhancements

- [ ] Global state with Redux/Zustand for complex state
- [ ] PWA features (offline support, install app)
- [ ] Advanced filtering and search
- [ ] User favorites and preferences
- [ ] Shopping list generation
- [ ] Nutrition tracking dashboard
- [ ] Social features (sharing meals, reviews)
- [ ] Push notifications for meal recommendations

## 🤝 Contributing

This is a production-ready template. Customize it for your needs!

## 📄 License

MIT License - Feel free to use for your projects

## 📞 Support

For questions about the architecture, see:
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed architecture
- [API_INTEGRATION.md](./API_INTEGRATION.md) - Backend integration
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Detailed structure

# Backend Integration Guide

This guide explains how to connect this frontend to your backend API.

## 📋 Overview

The frontend is designed to work with any backend. Mock data currently provides working functionality, which can be replaced with real API calls.

## 🔄 Integration Steps

### Step 1: Update Environment Variables

Create `.env` file in project root:

```env
REACT_APP_API_URL=https://api.yourbackend.com
REACT_APP_API_VERSION=v1
REACT_APP_ENV=production
```

Use in code:
```typescript
const apiUrl = process.env.REACT_APP_API_URL;
```

### Step 2: Update API Client

Replace mock implementation in `src/services/api/client.ts`:

```typescript
// Before:
const response = await mockAuthResponse(email, password);

// After:
const response = await apiClient.post<LoginResponse>('/auth/login', {
  email,
  password,
});
```

### Step 3: Replace Service Implementations

Each service class has TODO comments showing where to replace mock data:

#### Authentication Service (`src/services/auth/authService.ts`)

```typescript
// Before (MOCK):
async login(credentials: LoginCredentials): Promise<LoginResponse> {
  await new Promise((resolve) => setTimeout(resolve, API_DELAY));
  const result = await mockAuthResponse(credentials.email, credentials.password);
  // ... mock logic
}

// After (REAL API):
async login(credentials: LoginCredentials): Promise<LoginResponse> {
  try {
    const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
    
    if (response.success && response.data?.token) {
      localStorage.setItem('auth_token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      return {
        success: true,
        user: response.data.user,
        token: response.data.token,
      };
    }
    
    return {
      success: false,
      message: response.error?.message || 'Login failed',
    };
  } catch (error) {
    return {
      success: false,
      message: error instanceof Error ? error.message : 'An error occurred',
    };
  }
}
```

#### Recipe Service (`src/services/recipe/recipeService.ts`)

```typescript
// Before (MOCK):
async getRecipes(): Promise<Recipe[]> {
  await new Promise((resolve) => setTimeout(resolve, API_DELAY));
  return mockRecipes;
}

// After (REAL API):
async getRecipes(): Promise<Recipe[]> {
  try {
    const response = await apiClient.get<Recipe[]>('/recipes');
    return response.data || [];
  } catch (error) {
    console.error('Failed to fetch recipes:', error);
    throw error;
  }
}
```

#### Meal Service (`src/services/recipe/mealService.ts`)

```typescript
// Replace with your AI recommendation API
async getMealSuggestions(): Promise<MealSuggestion[]> {
  try {
    const userProfile = authService.getCurrentUser()?.profile;
    
    const response = await apiClient.post<MealSuggestion[]>(
      '/meals/suggest',
      { userProfile }
    );
    
    return response.data || [];
  } catch (error) {
    console.error('Failed to fetch meal suggestions:', error);
    throw error;
  }
}
```

## 🔐 Authentication & Token Management

### JWT Token Handling

The API client automatically includes auth tokens:

```typescript
// In api/client.ts
const token = localStorage.getItem('auth_token');
if (token) {
  headers['Authorization'] = `Bearer ${token}`;
}
```

### Token Refresh Strategy

Add token refresh logic:

```typescript
// In api/client.ts
private async request<T>(...) {
  // ... existing code
  
  if (response.status === 401) {
    // Token expired, try to refresh
    const refreshed = await this.refreshToken();
    if (refreshed) {
      // Retry original request
      return this.request<T>(endpoint, options);
    } else {
      // Redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
  }
}

private async refreshToken(): Promise<boolean> {
  // Call your refresh token endpoint
  const response = await fetch(`${this.baseURL}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('auth_token', data.token);
    return true;
  }
  
  return false;
}
```

## 📡 API Endpoint Mapping

### Expected Backend Endpoints

#### Authentication
```
POST   /auth/login                 - User login
POST   /auth/logout                - User logout
POST   /auth/refresh               - Refresh token
POST   /auth/register              - User registration
```

#### Users
```
GET    /users/profile              - Get current user profile
PUT    /users/profile              - Update user profile
POST   /users/onboarding/complete  - Complete onboarding
```

#### Recipes
```
GET    /recipes                    - Get all recipes
GET    /recipes/:id                - Get recipe by ID
GET    /recipes/search?q=...       - Search recipes
POST   /recipes                    - Create new recipe
PUT    /recipes/:id                - Update recipe
DELETE /recipes/:id                - Delete recipe
```

#### Saved Recipes
```
GET    /saved-recipes              - Get user's saved recipes
POST   /saved-recipes              - Save recipe
DELETE /saved-recipes/:id          - Remove saved recipe
GET    /saved-recipes/user         - Get current user's saved recipes
```

#### Meals
```
POST   /meals/suggest              - Get AI meal suggestions
GET    /meals/plan?date=...        - Get meal plan for date
POST   /meals/plan                 - Save meal plan
```

## 🔍 Error Handling

### Standard Error Response Format

```typescript
// Backend should return:
{
  success: false,
  error: {
    code: 'ERROR_CODE',
    message: 'Human readable error message'
  }
}

// Or for errors:
{
  statusCode: 400,
  error: 'Bad Request',
  message: 'Invalid input'
}
```

### Frontend Error Handling

```typescript
async get<T>(endpoint: string): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP Error: ${response.status}`);
    }
    
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: {
        code: 'API_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
    };
  }
}
```

## 📦 Data Model Examples

### User Profile (from Onboarding)

```json
{
  "id": "user-123",
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "isOnboarded": true,
  "profile": {
    "age": 28,
    "height": 180,
    "weight": 75,
    "gender": "male",
    "activityLevel": "high",
    "healthCondition": "No conditions"
  }
}
```

### Recipe

```json
{
  "id": "recipe-1",
  "title": "Grilled Chicken with Quinoa",
  "description": "Healthy grilled chicken...",
  "image": "https://...",
  "calories": 450,
  "protein": 45,
  "carbs": 35,
  "fat": 12,
  "servings": 2,
  "prepTime": 15,
  "cookTime": 20,
  "difficulty": "easy",
  "ingredients": [...],
  "instructions": [...]
}
```

### Meal Suggestion

```json
{
  "id": "suggestion-1",
  "recipe": {
    "id": "recipe-1",
    "title": "Grilled Chicken",
    "image": "https://...",
    "calories": 450,
    "protein": 45,
    "carbs": 35,
    "fat": 12
  },
  "reason": "High protein, matches your fitness goals"
}
```

## 🧪 Testing with Backend

### Using Postman/Insomnia

1. Create environment variables in Postman
2. Test all endpoints
3. Ensure response format matches frontend expectations
4. Document any differences from the frontend types

### API Contract Validation

Ensure backend responses match TypeScript types:

```typescript
// If type expects:
interface Recipe {
  id: string;
  title: string;
  calories: number;
}

// Backend must return:
{
  "id": "string",
  "title": "string",
  "calories": number
}
```

## 🚀 Deployment Checklist

- [ ] Update REACT_APP_API_URL for production
- [ ] Test all API endpoints on staging
- [ ] Implement token refresh logic
- [ ] Add error monitoring (Sentry, etc.)
- [ ] Enable CORS properly on backend
- [ ] Test authentication flow end-to-end
- [ ] Verify HTTPS/SSL setup
- [ ] Test on mobile devices
- [ ] Clear browser cache during testing
- [ ] Monitor API response times

## 🔗 Useful Resources

- [API Client Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [REST API Design Guidelines](https://restfulapi.net/)
- [JWT Authentication](https://jwt.io/introduction)
- [CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

## 💡 Pro Tips

1. **Gradual Migration**: Replace mock data one service at a time
2. **Keep Mock Data**: Useful for testing when backend is down
3. **Error Messages**: Use backend error messages in UI
4. **Loading States**: Frontend hooks handle loading states automatically
5. **Cache Strategy**: Consider implementing caching for recipes
6. **Rate Limiting**: Implement request debouncing if needed
7. **Logging**: Add request/response logging in development
8. **TypeScript**: Keep types in sync with backend

## 📞 Common Issues

### CORS Errors
```
Solution: Configure CORS on backend
Access-Control-Allow-Origin: https://yourdomain.com
```

### 401 Unauthorized
```
Solution: Check token is being sent and is valid
```

### 404 Not Found
```
Solution: Verify endpoint path matches backend route
```

### Network Timeout
```
Solution: Increase timeout, check backend performance
```

## ✅ Integration Checklist

After connecting to backend:

- [ ] All pages load without errors
- [ ] Login works with real credentials
- [ ] Onboarding saves to backend
- [ ] Dashboard loads user's data
- [ ] Recipes load from API
- [ ] Saving recipes works
- [ ] Profile updates save
- [ ] Logout clears session
- [ ] Error handling works
- [ ] Token refresh works

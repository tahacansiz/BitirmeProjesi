/**
 * API Endpoints
 * Centralized endpoint definitions
 * Easy to update when backend is ready
 */

export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    REGISTER: '/auth/register',
  },

  // User endpoints
  USERS: {
    PROFILE: '/users/profile',
    UPDATE_PROFILE: '/users/profile',
    ONBOARDING: '/users/onboarding',
    ONBOARDING_COMPLETE: '/users/onboarding/complete',
  },

  // Recipe endpoints
  RECIPES: {
    LIST: '/recipes',
    GET: (id: string) => `/recipes/${id}`,
    CREATE: '/recipes',
    UPDATE: (id: string) => `/recipes/${id}`,
    DELETE: (id: string) => `/recipes/${id}`,
    SEARCH: '/recipes/search',
  },

  // Saved recipes endpoints
  SAVED_RECIPES: {
    LIST: '/saved-recipes',
    ADD: '/saved-recipes',
    REMOVE: (id: string) => `/saved-recipes/${id}`,
    GET_USER_SAVED: '/saved-recipes/user',
  },

  // Meal suggestions endpoints
  MEALS: {
    SUGGEST: '/meals/suggest',
    GET_PLAN: '/meals/plan',
    SAVE_PLAN: '/meals/plan',
  },
};

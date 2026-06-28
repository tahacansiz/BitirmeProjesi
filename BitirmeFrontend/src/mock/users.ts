/**
 * Mock User Data
 * Simulates user profiles and authentication responses
 */

import type { User } from '../types/auth';

export const mockUsers: User[] = [
  {
    id: 'user-1',
    email: 'john@example.com',
    firstName: 'John',
    lastName: 'Doe',
    isOnboarded: true,
    profile: {
      age: 28,
      height: 180,
      weight: 75,
      gender: 'male',
      activityLevel: 'high',
      healthCondition: 'No conditions',
      createdAt: '2024-01-15',
      updatedAt: '2024-04-10',
    },
  },
  {
    id: 'user-2',
    email: 'jane@example.com',
    firstName: 'Jane',
    lastName: 'Smith',
    isOnboarded: false,
    profile: undefined,
  },
];

/**
 * Simulate API delay for more realistic behavior
 */
export const simulateApiDelay = (ms: number = 500): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Mock authentication helper
 */
export const mockAuthResponse = async (
  email: string,
  password: string
): Promise<{ success: boolean; user?: User; error?: string }> => {
  await simulateApiDelay();

  const user = mockUsers.find((u) => u.email === email);

  if (!user) {
    return { success: false, error: 'User not found' };
  }

  if (password !== 'password123') {
    return { success: false, error: 'Invalid password' };
  }

  return {
    success: true,
    user,
  };
};

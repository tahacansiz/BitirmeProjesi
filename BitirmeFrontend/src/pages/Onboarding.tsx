/**
 * Onboarding Page
 * First-time user setup flow
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useOnboarding, useAuthStatus } from '../hooks/useAuth';
import { OnboardingForm } from '../components/auth/OnboardingForm';
import '../styles/pages.css';

export const OnboardingPage: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuthStatus();
  const { isOnboarded, needsOnboarding } = useOnboarding();

  // Redirect to login if not authenticated
  if (!isAuthenticated && !authLoading) {
    return <Navigate to="/login" replace />;
  }

  // Redirect to dashboard if already onboarded
  if (isOnboarded) {
    return <Navigate to="/dashboard" replace />;
  }

  // Show onboarding form
  if (needsOnboarding || !authLoading) {
    return (
      <div className="onboarding-page">
        <div className="onboarding-page__container">
          <OnboardingForm />
        </div>
      </div>
    );
  }

  return null;
};

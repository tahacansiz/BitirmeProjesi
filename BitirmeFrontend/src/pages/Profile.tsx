/**
 * Profile Page
 * User profile management and settings
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStatus, useOnboarding } from '../hooks/useAuth';
import { ProfileForm } from '../components/profile/ProfileForm';
import '../styles/pages.css';

export const ProfilePage: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuthStatus();
  const { needsOnboarding } = useOnboarding();

  // Redirect if not authenticated
  if (!isAuthenticated && !authLoading) {
    return <Navigate to="/login" replace />;
  }

  // Redirect if onboarding not completed
  if (needsOnboarding && !authLoading) {
    return <Navigate to="/onboarding" replace />;
  }

  return (
    <div className="profile-page">
      <div className="profile-page__container">
        <ProfileForm />
      </div>
    </div>
  );
};

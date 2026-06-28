/**
 * Login Page
 * Initial authentication screen
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStatus } from '../hooks/useAuth';
import { LoginForm } from '../components/auth/LoginForm';
import '../styles/pages.css';

export const LoginPage: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuthStatus();

  // Redirect to dashboard if already logged in
  if (isAuthenticated && !isLoading) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="login-page">
      <div className="login-page__container">
        <LoginForm />
      </div>
    </div>
  );
};

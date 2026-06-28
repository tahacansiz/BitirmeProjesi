/**
 * Auth Layout
 * Layout for authentication pages (login, onboarding)
 */

import React from 'react';
import '../styles/layouts.css';

interface AuthLayoutProps {
  children: React.ReactNode;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="auth-layout">
      <div className="auth-layout__background"></div>
      <div className="auth-layout__content">
        {children}
      </div>
    </div>
  );
};

/**
 * Login Form Component
 * Handles user authentication
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';
import '../../styles/components.css';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('john@example.com'); // Pre-filled for demo
  const [password, setPassword] = useState('password123'); // Pre-filled for demo
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const { login, isLoading, error: authError, clearError } = useAuth();
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!email) errors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) errors.email = 'Email is invalid';

    if (!password) errors.password = 'Password is required';
    else if (password.length < 6) errors.password = 'Password must be at least 6 characters';

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      await login({ email, password });
      navigate('/');
    } catch (err) {
      // Error is already in auth context
    }
  };

  return (
    <div className="login-form">
      <h1 className="login-form__title">Welcome to NutriFlow</h1>
      <p className="login-form__subtitle">Your personal nutrition guide</p>

      <form onSubmit={handleSubmit} className="login-form__form">
        {authError && (
          <Alert
            type="error"
            message={authError}
            onClose={clearError}
            autoClose={false}
          />
        )}

        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={validationErrors.email}
          placeholder="your@email.com"
          disabled={isLoading}
        />

        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={validationErrors.password}
          placeholder="••••••••"
          disabled={isLoading}
          helpText="Demo: password123"
        />

        <Button
          type="submit"
          variant="primary"
          size="large"
          fullWidth
          isLoading={isLoading}
        >
          Sign In
        </Button>
      </form>

      <div className="login-form__footer">
        <p className="login-form__demo-info">
          Demo credentials (for testing):
          <br />
          Email: john@example.com
          <br />
          Password: password123
        </p>
      </div>
    </div>
  );
};

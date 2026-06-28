/**
 * Onboarding Form Component
 * Collects user health information for personalization
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';
import { authService } from '../../services/auth/authService';
import '../../styles/components.css';

export const OnboardingForm: React.FC = () => {
  const [age, setAge] = useState('');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [gender, setGender] = useState<'male' | 'female' | 'other'>('male');
  const [activityLevel, setActivityLevel] = useState<'low' | 'medium' | 'high'>('medium');
  const [healthCondition, setHealthCondition] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const navigate = useNavigate();
  const { user } = useAuth();

  const validateForm = (): boolean => {
    const formErrors: Record<string, string> = {};

    if (!age || parseInt(age) < 13 || parseInt(age) > 120) {
      formErrors.age = 'Please enter a valid age (13-120)';
    }

    if (!height || parseInt(height) < 100 || parseInt(height) > 250) {
      formErrors.height = 'Please enter height in cm (100-250)';
    }

    if (!weight || parseInt(weight) < 30 || parseInt(weight) > 300) {
      formErrors.weight = 'Please enter weight in kg (30-300)';
    }

    setErrors(formErrors);
    return Object.keys(formErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm() || !user) return;

    setIsLoading(true);
    setSubmitError(null);

    try {
      const success = await authService.completeOnboarding({
        age: parseInt(age),
        height: parseInt(height),
        weight: parseInt(weight),
        gender,
        activityLevel,
        healthCondition,
      });

      if (success) {
        navigate('/dashboard');
      } else {
        setSubmitError('Failed to complete onboarding. Please try again.');
      }
    } catch (err) {
      setSubmitError(
        err instanceof Error ? err.message : 'An error occurred'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="onboarding-form">
      <div className="onboarding-form__header">
        <h1 className="onboarding-form__title">Get Started</h1>
        <p className="onboarding-form__subtitle">
          Tell us about yourself so we can personalize your nutrition plan
        </p>
      </div>

      <form onSubmit={handleSubmit} className="onboarding-form__form">
        {submitError && (
          <Alert
            type="error"
            message={submitError}
            onClose={() => setSubmitError(null)}
            autoClose={false}
          />
        )}

        <div className="onboarding-form__section">
          <h2 className="onboarding-form__section-title">Personal Information</h2>

          <Input
            label="Age"
            type="number"
            min="13"
            max="120"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            error={errors.age}
            disabled={isLoading}
          />

          <div className="onboarding-form__row">
            <Input
              label="Height (cm)"
              type="number"
              min="100"
              max="250"
              value={height}
              onChange={(e) => setHeight(e.target.value)}
              error={errors.height}
              disabled={isLoading}
            />

            <Input
              label="Weight (kg)"
              type="number"
              min="30"
              max="300"
              step="0.1"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              error={errors.weight}
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="onboarding-form__section">
          <h2 className="onboarding-form__section-title">Lifestyle</h2>

          <div className="onboarding-form__group">
            <label className="onboarding-form__label">Gender</label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value as any)}
              className="onboarding-form__select"
              disabled={isLoading}
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="onboarding-form__group">
            <label className="onboarding-form__label">Activity Level</label>
            <select
              value={activityLevel}
              onChange={(e) => setActivityLevel(e.target.value as any)}
              className="onboarding-form__select"
              disabled={isLoading}
            >
              <option value="low">Low (sedentary)</option>
              <option value="medium">Medium (lightly active)</option>
              <option value="high">High (very active)</option>
            </select>
          </div>
        </div>

        <div className="onboarding-form__section">
          <h2 className="onboarding-form__section-title">Health</h2>

          <Input
            label="Health Conditions (e.g., diabetes, allergies)"
            type="text"
            value={healthCondition}
            onChange={(e) => setHealthCondition(e.target.value)}
            placeholder="None / Type 2 Diabetes / Nut Allergies"
            disabled={isLoading}
          />
        </div>

        <Button
          type="submit"
          variant="primary"
          size="large"
          fullWidth
          isLoading={isLoading}
        >
          Complete Setup
        </Button>
      </form>
    </div>
  );
};

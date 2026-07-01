import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';
import '../../styles/components.css';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const { login, isLoading, error: authError, clearError } = useAuth();
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!email) errors.email = 'E-posta adresi gereklidir';
    else if (!/\S+@\S+\.\S+/.test(email)) errors.email = 'Geçerli bir e-posta adresi giriniz';

    if (!password) errors.password = 'Şifre gereklidir';
    else if (password.length < 6) errors.password = 'Şifre en az 6 karakter olmalıdır';

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    try {
      await login({ email, password });
      navigate('/');
    } catch (err) {}
  };

  return (
    <div className="login-form">
      <h1 className="login-form__title">NutriFlow'a Hoş Geldiniz</h1>
      <p className="login-form__subtitle">Kişisel beslenme rehberiniz</p>

      <form onSubmit={handleSubmit} className="login-form__form">
        {authError && (
          <Alert
            type="error"
            message="E-posta veya şifre hatalı"
            onClose={clearError}
            autoClose={false}
          />
        )}

        <Input
          label="E-posta"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={validationErrors.email}
          placeholder="ornek@email.com"
          disabled={isLoading}
        />

        <Input
          label="Şifre"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={validationErrors.password}
          placeholder="••••••••"
          disabled={isLoading}
        />

        <Button type="submit" variant="primary" size="large" fullWidth isLoading={isLoading}>
          Giriş Yap
        </Button>
      </form>

      <div className="login-form__footer">
        <p className="login-form__demo-info">
          Test hesabı: test@test.com / 123456
        </p>
      </div>
    </div>
  );
};

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
  const { user, refreshUser } = useAuth();

  const validateForm = (): boolean => {
    const formErrors: Record<string, string> = {};

    if (!age || parseInt(age) < 13 || parseInt(age) > 120)
      formErrors.age = 'Lütfen geçerli bir yaş giriniz (13-120)';

    if (!height || parseInt(height) < 100 || parseInt(height) > 250)
      formErrors.height = 'Lütfen boy bilgisini cm cinsinden giriniz (100-250)';

    if (!weight || parseInt(weight) < 30 || parseInt(weight) > 300)
      formErrors.weight = 'Lütfen kilo bilgisini kg cinsinden giriniz (30-300)';

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
        refreshUser();
        navigate('/dashboard');
      } else {
        setSubmitError('Kurulum tamamlanamadı. Lütfen tekrar deneyin.');
      }
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Bir hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="onboarding-form">
      <div className="onboarding-form__header">
        <h1 className="onboarding-form__title">Başlayalım</h1>
        <p className="onboarding-form__subtitle">
          Size özel beslenme planı oluşturabilmemiz için birkaç bilgiye ihtiyacımız var
        </p>
      </div>

      <form onSubmit={handleSubmit} className="onboarding-form__form">
        {submitError && (
          <Alert type="error" message={submitError} onClose={() => setSubmitError(null)} autoClose={false} />
        )}

        <div className="onboarding-form__section">
          <h2 className="onboarding-form__section-title">Kişisel Bilgiler</h2>

          <Input label="Yaş" type="number" min="13" max="120"
            value={age} onChange={(e) => setAge(e.target.value)}
            error={errors.age} disabled={isLoading} />

          <div className="onboarding-form__row">
            <Input label="Boy (cm)" type="number" min="100" max="250"
              value={height} onChange={(e) => setHeight(e.target.value)}
              error={errors.height} disabled={isLoading} />
            <Input label="Kilo (kg)" type="number" min="30" max="300" step="0.1"
              value={weight} onChange={(e) => setWeight(e.target.value)}
              error={errors.weight} disabled={isLoading} />
          </div>
        </div>

        <div className="onboarding-form__section">
          <h2 className="onboarding-form__section-title">Yaşam Tarzı</h2>

          <div className="onboarding-form__group">
            <label className="onboarding-form__label">Cinsiyet</label>
            <select value={gender} onChange={(e) => setGender(e.target.value as any)}
              className="onboarding-form__select" disabled={isLoading}>
              <option value="male">Erkek</option>
              <option value="female">Kadın</option>
              <option value="other">Diğer</option>
            </select>
          </div>

          <div className="onboarding-form__group">
            <label className="onboarding-form__label">Aktivite Düzeyi</label>
            <select value={activityLevel} onChange={(e) => setActivityLevel(e.target.value as any)}
              className="onboarding-form__select" disabled={isLoading}>
              <option value="low">Düşük (hareketsiz)</option>
              <option value="medium">Orta (hafif aktif)</option>
              <option value="high">Yüksek (çok aktif)</option>
            </select>
          </div>
        </div>

        <div className="onboarding-form__section">
          <h2 className="onboarding-form__section-title">Sağlık</h2>
          <Input
            label="Sağlık Durumları (örn: diyabet, çölyak)"
            type="text"
            value={healthCondition}
            onChange={(e) => setHealthCondition(e.target.value)}
            placeholder="Yok / Tip 2 Diyabet / Çölyak"
            disabled={isLoading}
          />
        </div>

        <Button type="submit" variant="primary" size="large" fullWidth isLoading={isLoading}>
          Kurulumu Tamamla
        </Button>
      </form>
    </div>
  );
};

import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { authService } from '../../services/auth/authService';
import { Alert } from '../common/Alert';
import '../../styles/components.css';

const GENDER_TR: Record<string, string> = {
  male: 'Erkek', female: 'Kadın', other: 'Diğer',
};
const ACTIVITY_TR: Record<string, string> = {
  low: 'Düşük', medium: 'Orta', high: 'Yüksek',
  sedentary: 'Hareketsiz', light: 'Hafif aktif', moderate: 'Orta aktif', vigorous: 'Çok aktif',
};
const GOAL_TR: Record<string, string> = {
  lose: 'Kilo ver', maintain: 'Koru', gain: 'Kilo al',
};

export const ProfileForm: React.FC = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const [formData, setFormData] = useState({
    age: user?.profile?.age?.toString() || '',
    height: user?.profile?.height?.toString() || '',
    weight: user?.profile?.weight?.toString() || '',
    gender: user?.profile?.gender || 'male',
    activityLevel: user?.profile?.activityLevel || 'medium',
    weightGoal: (user?.profile as any)?.weightGoal || 'maintain',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      const success = await authService.updateProfile({
        age: parseInt(formData.age),
        height: parseInt(formData.height),
        weight: parseFloat(formData.weight),
        gender: formData.gender,
        activityLevel: formData.activityLevel,
        healthCondition: '',
      });
      if (success) {
        setSuccessMessage('Profil başarıyla güncellendi!');
        setIsEditing(false);
      } else {
        setErrorMessage('Profil güncellenemedi. Lütfen tekrar deneyin.');
      }
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Bir hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user?.profile) {
    return <div>Profil yükleniyor...</div>;
  }

  return (
    <div className="profile-card">
      <div className="profile-card__header">
        <h2 className="profile-card__title">Profilim</h2>
        {!isEditing && (
          <button className="profile-card__edit-btn" onClick={() => setIsEditing(true)}>
            Profili Düzenle
          </button>
        )}
      </div>

      {successMessage && <Alert type="success" message={successMessage} onClose={() => setSuccessMessage('')} />}
      {errorMessage && <Alert type="error" message={errorMessage} onClose={() => setErrorMessage('')} autoClose={false} />}

      <form onSubmit={handleSubmit}>
        <section className="profile-card__section">
          <h3 className="profile-card__section-title">Kişisel Bilgiler</h3>
          <div className="profile-card__row">
            <div className="profile-card__field">
              <label className="profile-card__label">Yaş</label>
              {isEditing ? (
                <input className="profile-card__input" type="number" name="age" value={formData.age} onChange={handleChange} disabled={isLoading} />
              ) : (
                <div className="profile-card__value">{formData.age} yaş</div>
              )}
            </div>
            <div className="profile-card__field">
              <label className="profile-card__label">Boy</label>
              {isEditing ? (
                <input className="profile-card__input" type="number" name="height" value={formData.height} onChange={handleChange} disabled={isLoading} />
              ) : (
                <div className="profile-card__value">{formData.height} cm</div>
              )}
            </div>
          </div>
          <div className="profile-card__row">
            <div className="profile-card__field">
              <label className="profile-card__label">Kilo</label>
              {isEditing ? (
                <input className="profile-card__input" type="number" step="0.1" name="weight" value={formData.weight} onChange={handleChange} disabled={isLoading} />
              ) : (
                <div className="profile-card__value">{formData.weight} kg</div>
              )}
            </div>
          </div>
        </section>

        <div className="profile-card__divider" />

        <section className="profile-card__section">
          <h3 className="profile-card__section-title">Yaşam Tarzı</h3>
          <div className="profile-card__row">
            <div className="profile-card__field">
              <label className="profile-card__label">Cinsiyet</label>
              {isEditing ? (
                <select className="profile-card__input" name="gender" value={formData.gender} onChange={handleChange} disabled={isLoading}>
                  <option value="male">Erkek</option>
                  <option value="female">Kadın</option>
                  <option value="other">Diğer</option>
                </select>
              ) : (
                <div className="profile-card__value">{GENDER_TR[formData.gender] || formData.gender}</div>
              )}
            </div>
            <div className="profile-card__field">
              <label className="profile-card__label">Aktivite Düzeyi</label>
              {isEditing ? (
                <select className="profile-card__input" name="activityLevel" value={formData.activityLevel} onChange={handleChange} disabled={isLoading}>
                  <option value="low">Düşük</option>
                  <option value="medium">Orta</option>
                  <option value="high">Yüksek</option>
                </select>
              ) : (
                <div className="profile-card__value">{ACTIVITY_TR[formData.activityLevel] || formData.activityLevel}</div>
              )}
            </div>
          </div>
          <div className="profile-card__row">
            <div className="profile-card__field">
              <label className="profile-card__label">Kilo Hedefi</label>
              {isEditing ? (
                <select className="profile-card__input" name="weightGoal" value={formData.weightGoal} onChange={handleChange} disabled={isLoading}>
                  <option value="lose">Kilo ver</option>
                  <option value="maintain">Koru</option>
                  <option value="gain">Kilo al</option>
                </select>
              ) : (
                <div className="profile-card__value">{GOAL_TR[formData.weightGoal] || formData.weightGoal}</div>
              )}
            </div>
          </div>
        </section>

        {isEditing && (
          <div className="profile-card__actions">
            <button type="submit" className="profile-card__save-btn" disabled={isLoading}>
              {isLoading ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
            </button>
            <button type="button" className="profile-card__cancel-btn" onClick={() => setIsEditing(false)} disabled={isLoading}>
              İptal
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

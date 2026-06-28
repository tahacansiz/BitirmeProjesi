import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { authService } from '../../services/auth/authService';
import { Alert } from '../common/Alert';
import '../../styles/components.css';

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
        setSuccessMessage('Profile updated successfully!');
        setIsEditing(false);
      } else {
        setErrorMessage('Failed to update profile. Please try again.');
      }
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user?.profile) {
    return <div>Loading profile...</div>;
  }

  return (
    <div className="profile-card">
      <div className="profile-card__header">
        <h2 className="profile-card__title">My Profile</h2>
        {!isEditing ? (
          <button className="profile-card__edit-btn" onClick={() => setIsEditing(true)}>
            Edit Profile
          </button>
        ) : null}
      </div>

      {successMessage && (
        <Alert type="success" message={successMessage} onClose={() => setSuccessMessage('')} />
      )}
      {errorMessage && (
        <Alert type="error" message={errorMessage} onClose={() => setErrorMessage('')} autoClose={false} />
      )}

      <form onSubmit={handleSubmit}>
        <section className="profile-card__section">
          <h3 className="profile-card__section-title">Personal Information</h3>
          <div className="profile-card__row">
            <div className="profile-card__field">
              <label className="profile-card__label">Age</label>
              {isEditing ? (
                <input className="profile-card__input" type="number" name="age" value={formData.age} onChange={handleChange} disabled={isLoading} />
              ) : (
                <div className="profile-card__value">{formData.age} years</div>
              )}
            </div>
            <div className="profile-card__field">
              <label className="profile-card__label">Height</label>
              {isEditing ? (
                <input className="profile-card__input" type="number" name="height" value={formData.height} onChange={handleChange} disabled={isLoading} />
              ) : (
                <div className="profile-card__value">{formData.height} cm</div>
              )}
            </div>
          </div>
          <div className="profile-card__row">
            <div className="profile-card__field">
              <label className="profile-card__label">Weight</label>
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
          <h3 className="profile-card__section-title">Lifestyle</h3>
          <div className="profile-card__row">
            <div className="profile-card__field">
              <label className="profile-card__label">Gender</label>
              {isEditing ? (
                <select className="profile-card__input" name="gender" value={formData.gender} onChange={handleChange} disabled={isLoading}>
                  <option value="male">male</option>
                  <option value="female">female</option>
                  <option value="other">other</option>
                </select>
              ) : (
                <div className="profile-card__value">{formData.gender}</div>
              )}
            </div>
            <div className="profile-card__field">
              <label className="profile-card__label">Activity Level</label>
              {isEditing ? (
                <select className="profile-card__input" name="activityLevel" value={formData.activityLevel} onChange={handleChange} disabled={isLoading}>
                  <option value="low">low</option>
                  <option value="medium">medium</option>
                  <option value="high">high</option>
                </select>
              ) : (
                <div className="profile-card__value">{formData.activityLevel}</div>
              )}
            </div>
          </div>
          <div className="profile-card__row">
            <div className="profile-card__field">
              <label className="profile-card__label">Weight Goal</label>
              {isEditing ? (
                <select className="profile-card__input" name="weightGoal" value={formData.weightGoal} onChange={handleChange} disabled={isLoading}>
                  <option value="lose">lose</option>
                  <option value="maintain">maintain</option>
                  <option value="gain">gain</option>
                </select>
              ) : (
                <div className="profile-card__value">{formData.weightGoal}</div>
              )}
            </div>
          </div>
        </section>

        {isEditing && (
          <div className="profile-card__actions">
            <button type="submit" className="profile-card__save-btn" disabled={isLoading}>
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
            <button type="button" className="profile-card__cancel-btn" onClick={() => setIsEditing(false)} disabled={isLoading}>
              Cancel
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

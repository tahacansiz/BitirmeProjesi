/**
 * Loading Spinner
 * Reusable loading indicator
 */

import React from 'react';
import '../../styles/components.css';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  message,
}) => {
  return (
    <div className="loading-spinner" data-size={size}>
      <div className="loading-spinner__spinner"></div>
      {message && <p className="loading-spinner__message">{message}</p>}
    </div>
  );
};

/**
 * Input Component
 * Reusable form input field
 */

import React from 'react';
import '../../styles/components.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helpText?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helpText,
  className,
  id,
  ...props
}) => {
  const uniqueId = id || `input-${Math.random()}`;

  return (
    <div className="input-group">
      {label && (
        <label htmlFor={uniqueId} className="input-group__label">
          {label}
        </label>
      )}
      <input
        id={uniqueId}
        className={`input ${error ? 'input--error' : ''} ${className || ''}`}
        {...props}
      />
      {error && <span className="input-group__error">{error}</span>}
      {helpText && <span className="input-group__help">{helpText}</span>}
    </div>
  );
};

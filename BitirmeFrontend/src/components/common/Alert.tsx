/**
 * Alert Component
 * Display notifications and messages
 */

import React, { useEffect } from 'react';
import '../../styles/components.css';

interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  onClose?: () => void;
  autoClose?: boolean;
  autoCloseDelay?: number;
}

export const Alert: React.FC<AlertProps> = ({
  type,
  message,
  onClose,
  autoClose = true,
  autoCloseDelay = 5000,
}) => {
  useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(onClose, autoCloseDelay);
      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseDelay, onClose]);

  return (
    <div className={`alert alert--${type}`}>
      <div className="alert__content">
        <span className="alert__icon"></span>
        <span className="alert__message">{message}</span>
      </div>
      {onClose && (
        <button className="alert__close" onClick={onClose}>
          ✕
        </button>
      )}
    </div>
  );
};

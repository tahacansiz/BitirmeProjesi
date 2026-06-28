import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import '../../styles/components.css';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    setIsMenuOpen(false);
  };

  return (
    <header className="header">
      <div className="header__container">
        <Link to="/" className="header__logo">
          <span className="header__logo-icon">🥗</span>
          <span className="header__logo-text">NutriFlow</span>
        </Link>

        <div className="header__user">
          {user && (
            <div className="header__menu">
              <button
                className="header__avatar-btn"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                aria-label="User menu"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2"/>
                  <path d="M4 20c0-4 3.582-7 8-7s8 3 8 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
              {isMenuOpen && (
                <div className="header__dropdown">
                  <button
                    onClick={() => { navigate('/profile'); setIsMenuOpen(false); }}
                    className="header__dropdown-item"
                  >
                    My Profile
                  </button>
                  <button
                    onClick={handleLogout}
                    className="header__dropdown-item header__dropdown-item--danger"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};


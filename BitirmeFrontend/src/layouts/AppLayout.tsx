import React from 'react';
import { Header } from '../components/common/Header';
import '../styles/layouts.css';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="app-layout">
      <Header />
      <main className="app-layout__main">
        {children}
      </main>
    </div>
  );
};


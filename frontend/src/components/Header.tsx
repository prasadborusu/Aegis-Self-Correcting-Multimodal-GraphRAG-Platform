import React from 'react';
import { Shield } from 'lucide-react';
import { NavigationTab, HealthResponse } from '../types';

interface HeaderProps {
  currentTab: NavigationTab;
  onTabChange: (tab: NavigationTab) => void;
  health: HealthResponse | null;
  loadingHealth: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onTabChange,
  health,
  loadingHealth,
}) => {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/20">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-xl tracking-tight text-slate-900">AEGIS</span>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-blue-50 text-blue-700 border border-blue-200/60">
                  v{health?.version || '0.1.0'}
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-slate-100 text-slate-600 border border-slate-200">
                  AWS {health?.region || 'ap-south-1'}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium hidden sm:block">
                Evidence-First Knowledge Intelligence Platform
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 sm:space-x-2">
            <button
              onClick={() => onTabChange('dashboard')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'dashboard'
                  ? 'bg-blue-50 text-blue-700 border border-blue-200/80 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => onTabChange('documents')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'documents'
                  ? 'bg-blue-50 text-blue-700 border border-blue-200/80 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
              }`}
            >
              Documents
            </button>
            <button
              onClick={() => onTabChange('ask')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
                currentTab === 'ask'
                  ? 'bg-blue-50 text-blue-700 border border-blue-200/80 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
              }`}
            >
              Ask Aegis
            </button>
          </nav>

          {/* System Status Pill */}
          <div className="flex items-center space-x-3">
            <div
              className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium border ${
                loadingHealth
                  ? 'bg-slate-50 text-slate-500 border-slate-200'
                  : isHealthy
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}
              title={
                health
                  ? `Backend connected: ${health.service} (${health.status})`
                  : 'Connecting to backend...'
              }
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  loadingHealth
                    ? 'bg-slate-400 animate-pulse'
                    : isHealthy
                    ? 'bg-emerald-500'
                    : 'bg-amber-500'
                }`}
              />
              <span className="hidden md:inline">
                {loadingHealth ? 'Checking...' : isHealthy ? 'Engine Online' : 'Engine Standby'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

import React, { useState, useEffect, useCallback } from 'react';
import { NavigationTab, HealthResponse, DashboardMetrics, DocumentItem } from '../types';
import { Header } from '../components/Header';
import { DashboardPage } from '../pages/DashboardPage';
import { DocumentsPage } from '../pages/DocumentsPage';
import { AskAegisPage } from '../pages/AskAegisPage';
import { fetchHealth, fetchDashboardMetrics, fetchDocuments } from '../services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavigationTab>('dashboard');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    documentsProcessed: null,
    totalChunks: null,
    indexedSources: null,
    totalQueries: null,
    avgRetrievalLatencyMs: null,
    avgGenerationLatencyMs: null,
    groundingRate: null,
    selfCorrectionRate: null,
    failedIngestionJobs: null,
  });
  const [documents, setDocuments] = useState<DocumentItem[]>([]);

  const loadData = useCallback(async () => {
    setLoadingHealth(true);
    try {
      const [healthData, metricsData, docsData] = await Promise.all([
        fetchHealth().catch(() => null),
        fetchDashboardMetrics(),
        fetchDocuments(),
      ]);

      if (healthData) {
        setHealth(healthData);
      }
      setMetrics(metricsData);
      setDocuments(docsData);
    } finally {
      setLoadingHealth(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      <Header
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        health={health}
        loadingHealth={loadingHealth}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentTab === 'dashboard' && (
          <DashboardPage
            health={health}
            metrics={metrics}
            onNavigate={setCurrentTab}
          />
        )}
        {currentTab === 'documents' && (
          <DocumentsPage
            documents={documents}
            onRefresh={loadData}
          />
        )}
        {currentTab === 'ask' && <AskAegisPage />}
      </main>

      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-800">Aegis Intelligence</span>
            <span>— Built for AWS Zero to Shipped Hackathon</span>
          </div>
          <div className="text-slate-400">
            Upload → Understand → Retrieve → Reason → Verify → Correct → Cite
          </div>
        </div>
      </footer>
    </div>
  );
};

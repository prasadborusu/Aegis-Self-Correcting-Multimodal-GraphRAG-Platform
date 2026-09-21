import React from 'react';
import {
  FileText,
  Layers,
  Search,
  MessageSquare,
  Clock,
  Cpu,
  ShieldCheck,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { DashboardMetrics } from '../types';

interface MetricsCardsProps {
  metrics: DashboardMetrics;
}

interface MetricItem {
  id: string;
  label: string;
  value: string | null;
  raw: number | null;
  unit?: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  status?: 'normal' | 'warning' | 'positive';
}

export const MetricsCards: React.FC<MetricsCardsProps> = ({ metrics }) => {
  const items: MetricItem[] = [
    {
      id: 'docs',
      label: 'Documents Processed',
      raw: metrics.documentsProcessed,
      value: metrics.documentsProcessed !== null ? metrics.documentsProcessed.toLocaleString() : null,
      icon: FileText,
      description: 'Ingested into S3 & OpenSearch',
    },
    {
      id: 'chunks',
      label: 'Total Chunks',
      raw: metrics.totalChunks,
      value: metrics.totalChunks !== null ? metrics.totalChunks.toLocaleString() : null,
      icon: Layers,
      description: 'Structure-aware indexed chunks',
    },
    {
      id: 'sources',
      label: 'Indexed Sources',
      raw: metrics.indexedSources,
      value: metrics.indexedSources !== null ? metrics.indexedSources.toLocaleString() : null,
      icon: Search,
      description: 'Active knowledge documents',
    },
    {
      id: 'queries',
      label: 'Total Queries',
      raw: metrics.totalQueries,
      value: metrics.totalQueries !== null ? metrics.totalQueries.toLocaleString() : null,
      icon: MessageSquare,
      description: 'Knowledge inquiries processed',
    },
    {
      id: 'retrieval-latency',
      label: 'Avg Retrieval Latency',
      raw: metrics.avgRetrievalLatencyMs,
      value: metrics.avgRetrievalLatencyMs !== null ? `${metrics.avgRetrievalLatencyMs} ms` : null,
      icon: Clock,
      description: 'Vector & hybrid retrieval roundtrip',
    },
    {
      id: 'generation-latency',
      label: 'Avg Generation Latency',
      raw: metrics.avgGenerationLatencyMs,
      value: metrics.avgGenerationLatencyMs !== null ? `${metrics.avgGenerationLatencyMs} ms` : null,
      icon: Cpu,
      description: 'Bedrock generation duration',
    },
    {
      id: 'grounding-rate',
      label: 'Grounding Rate',
      raw: metrics.groundingRate,
      value: metrics.groundingRate !== null ? `${(metrics.groundingRate * 100).toFixed(1)}%` : null,
      icon: ShieldCheck,
      description: 'Claim verification fidelity',
      status: metrics.groundingRate !== null && metrics.groundingRate >= 0.8 ? 'positive' : 'normal',
    },
    {
      id: 'self-correction-rate',
      label: 'Self-Correction Rate',
      raw: metrics.selfCorrectionRate,
      value: metrics.selfCorrectionRate !== null ? `${(metrics.selfCorrectionRate * 100).toFixed(1)}%` : null,
      icon: RefreshCw,
      description: 'Queries requiring re-retrieval loop',
    },
    {
      id: 'failed-jobs',
      label: 'Failed Ingestion Jobs',
      raw: metrics.failedIngestionJobs,
      value: metrics.failedIngestionJobs !== null ? metrics.failedIngestionJobs.toLocaleString() : null,
      icon: AlertCircle,
      description: 'Extraction or embedding errors',
      status: metrics.failedIngestionJobs !== null && metrics.failedIngestionJobs > 0 ? 'warning' : 'normal',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((item) => {
        const Icon = item.icon;
        const hasData = item.value !== null;

        return (
          <div
            key={item.id}
            className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                {item.label}
              </span>
              <div className="w-8 h-8 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-600">
                <Icon className="w-4 h-4 text-blue-600" />
              </div>
            </div>

            <div className="flex items-baseline space-x-2">
              {hasData ? (
                <div className="text-2xl font-bold text-slate-900 tracking-tight">
                  {item.value}
                </div>
              ) : (
                <div className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
                  No data yet
                </div>
              )}
            </div>

            <p className="text-xs text-slate-400 mt-2 font-normal">
              {item.description}
            </p>
          </div>
        );
      })}
    </div>
  );
};

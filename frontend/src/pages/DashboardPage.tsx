import React from 'react';
import {
  Shield,
  Upload,
  Search,
  Sparkles,
  Database,
} from 'lucide-react';
import { HealthResponse, DashboardMetrics, NavigationTab } from '../types';
import { MetricsCards } from '../components/MetricsCards';

interface DashboardPageProps {
  health: HealthResponse | null;
  metrics: DashboardMetrics;
  onNavigate: (tab: NavigationTab) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  health,
  metrics,
  onNavigate,
}) => {
  const subsystems = health?.subsystems;

  return (
    <div className="space-y-8">
      {/* Hero / Executive Overview Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs relative overflow-hidden">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AWS Zero to Shipped Hackathon Architecture</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Evidence-First Knowledge Intelligence
          </h1>
          <p className="mt-3 text-sm sm:text-base text-slate-600 leading-relaxed">
            Aegis is an enterprise RAG platform designed to eliminate hallucinations.
            It extracts structured evidence, verifies factual claims against source documents,
            and autonomously self-corrects retrieval when evidence is insufficient.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('documents')}
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-semibold bg-blue-600 text-white hover:bg-blue-700 shadow-xs transition-colors"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Document</span>
            </button>
            <button
              onClick={() => onNavigate('ask')}
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-semibold bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 transition-colors"
            >
              <Search className="w-4 h-4 text-blue-600" />
              <span>Ask Aegis Engine</span>
            </button>
          </div>
        </div>
      </div>

      {/* Real-time System Metrics */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-slate-900">
              Platform Telemetry & Performance
            </h2>
            <p className="text-xs text-slate-500">
              Live metrics aggregated from processing and verification runs
            </p>
          </div>
          <span className="text-xs text-slate-400 font-medium">
            Auto-refresh active
          </span>
        </div>
        <MetricsCards metrics={metrics} />
      </div>

      {/* Cloud Subsystems Configuration & Invariants */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AWS Infrastructure Spec */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center space-x-2 mb-4">
            <Database className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900 text-sm">
              Configured AWS Cloud Services
            </h3>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
              <span className="text-slate-500 font-medium">AWS Region</span>
              <span className="font-mono text-slate-800 font-semibold bg-slate-100 px-2 py-0.5 rounded">
                {health?.region || 'ap-south-1'}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
              <span className="text-slate-500 font-medium">S3 Knowledge Bucket</span>
              <span className="font-mono text-slate-700 text-right truncate max-w-xs">
                {subsystems?.s3?.documents_bucket || 'aegis-knowledge-sources-dev'}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
              <span className="text-slate-500 font-medium">Bedrock Embeddings</span>
              <span className="font-mono text-slate-700 text-right">
                {subsystems?.bedrock?.embedding_model || 'amazon.titan-embed-text-v2:0'}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
              <span className="text-slate-500 font-medium">Bedrock Generation LLM</span>
              <span className="font-mono text-slate-700 text-right">
                {subsystems?.bedrock?.generation_model || 'amazon.nova-pro-v1:0'}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
              <span className="text-slate-500 font-medium">DynamoDB Metadata Store</span>
              <span className="font-mono text-slate-700 text-right truncate max-w-xs">
                {subsystems?.dynamodb?.documents_table || 'aegis_documents_dev'}
              </span>
            </div>

            <div className="flex items-center justify-between py-2 text-xs">
              <span className="text-slate-500 font-medium">OpenSearch Vector Index</span>
              <span className="font-mono text-slate-700 text-right">
                {subsystems?.opensearch?.index || 'aegis-knowledge-index'}
              </span>
            </div>
          </div>
        </div>

        {/* Verification Engine Invariants */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center space-x-2 mb-4">
            <Shield className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900 text-sm">
              Architectural Invariants & Safeguards
            </h3>
          </div>

          <div className="space-y-4">
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80">
              <div className="flex justify-between items-center text-xs font-semibold text-slate-800 mb-1">
                <span>Self-Correction Safety Ceiling</span>
                <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-mono">
                  {subsystems?.verification_engine?.max_self_correction_attempts || 3} Iterations Max
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Prevents infinite query rewriting loops. If grounding cannot be achieved within 3 cycles,
                Aegis explicitly responds with insufficient evidence.
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80">
              <div className="flex justify-between items-center text-xs font-semibold text-slate-800 mb-1">
                <span>Grounding Acceptance Threshold</span>
                <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-mono">
                  {((subsystems?.verification_engine?.grounding_threshold ?? 0.75) * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Minimum claim-level verification coverage required before accepting a response.
                Unsubstantiated claims trigger automated query refinement.
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80">
              <div className="flex justify-between items-center text-xs font-semibold text-slate-800 mb-1">
                <span>Structure-Aware Chunking</span>
                <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded font-mono">
                  Preserves Context
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Never uses naive fixed slicing. Preserves page number, document section, headings,
                and provenance metadata for accurate citation generation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

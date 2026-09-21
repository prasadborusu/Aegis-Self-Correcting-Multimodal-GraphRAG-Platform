import React, { useState } from 'react';
import {
  Send,
  Shield,
  ShieldCheck,
  FileText,
  ChevronRight,
  Sparkles,
  X,
} from 'lucide-react';
import { Citation, ClaimVerification, RetrievalTrace } from '../types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  citations?: Citation[];
  groundingCoverage?: number;
  claims?: ClaimVerification[];
  trace?: RetrievalTrace;
}

export const AskAegisPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Welcome to Aegis. I am an evidence-first knowledge engine powered by Amazon Bedrock and OpenSearch. Ask any question against your uploaded sources. Every statement is verified for factual grounding against extracted document evidence before being presented.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [activeTrace, setActiveTrace] = useState<RetrievalTrace | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Add user message
    const userMsg: Message = {
      id: String(Date.now()),
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setQuery('');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Ask Aegis</h1>
        <p className="text-xs sm:text-sm text-slate-500">
          Query your knowledge base with verifiable claim-level grounding and automatic self-correcting retrieval.
        </p>
      </div>

      {/* Main Chat Stream */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 min-h-[460px] max-h-[600px] overflow-y-auto space-y-6 shadow-2xs">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl rounded-2xl p-4 sm:p-5 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white shadow-2xs'
                  : 'bg-slate-50 border border-slate-200/90 text-slate-800 shadow-2xs'
              }`}
            >
              {/* Message Header */}
              <div className="flex items-center justify-between mb-2 text-xs">
                <span
                  className={`font-semibold flex items-center space-x-1.5 ${
                    msg.role === 'user' ? 'text-blue-100' : 'text-slate-700'
                  }`}
                >
                  {msg.role === 'user' ? (
                    <span>You</span>
                  ) : (
                    <>
                      <Shield className="w-3.5 h-3.5 text-blue-600" />
                      <span>Aegis Intelligence Engine</span>
                    </>
                  )}
                </span>
                <span
                  className={`text-2xs ${
                    msg.role === 'user' ? 'text-blue-200' : 'text-slate-400'
                  }`}
                >
                  {msg.timestamp}
                </span>
              </div>

              {/* Message Body */}
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>

              {/* Factual Grounding & Citations Display for Assistant Messages */}
              {msg.role === 'assistant' && msg.groundingCoverage !== undefined && (
                <div className="mt-4 pt-3 border-t border-slate-200/80 space-y-3">
                  {/* Grounding Metric */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                      <span className="text-xs font-semibold text-slate-700">
                        Grounding Coverage: {(msg.groundingCoverage * 100).toFixed(0)}%
                      </span>
                    </div>

                    {msg.trace && (
                      <button
                        onClick={() => setActiveTrace(msg.trace || null)}
                        className="text-xs text-blue-600 hover:text-blue-700 font-medium inline-flex items-center space-x-1"
                      >
                        <span>How Aegis reached this answer</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    )}
                  </div>

                  {/* Citations List */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="space-y-1.5">
                      <span className="text-2xs font-semibold uppercase tracking-wider text-slate-400">
                        Supporting Evidence Citations
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {msg.citations.map((cite, i) => (
                          <button
                            key={i}
                            onClick={() => setSelectedCitation(cite)}
                            className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-medium bg-white border border-slate-200 hover:border-blue-300 text-slate-700 transition-colors shadow-2xs"
                          >
                            <FileText className="w-3 h-3 text-blue-600" />
                            <span>{cite.filename}</span>
                            {cite.page && (
                              <span className="text-slate-400 font-mono text-2xs">
                                p.{cite.page}
                              </span>
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Query Input Bar */}
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question against your uploaded documents..."
          className="w-full bg-white border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 rounded-xl px-4 py-3.5 pr-24 text-sm text-slate-900 placeholder-slate-400 shadow-2xs outline-none transition-all"
        />
        <div className="absolute right-2 top-2">
          <button
            type="submit"
            disabled={!query.trim()}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:hover:bg-blue-600 text-white shadow-2xs transition-colors"
          >
            <span>Ask</span>
            <Send className="w-3 h-3" />
          </button>
        </div>
      </form>

      {/* Citation Detail Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-2xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl border border-slate-200 max-w-lg w-full p-6 shadow-xl relative animate-in fade-in zoom-in-95 duration-150">
            <button
              onClick={() => setSelectedCitation(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1 rounded-md"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="flex items-center space-x-2 text-xs font-semibold text-blue-600 uppercase tracking-wider mb-2">
              <FileText className="w-4 h-4" />
              <span>Evidence Context Details</span>
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-1">
              {selectedCitation.filename}
            </h3>
            <div className="flex items-center space-x-3 text-xs text-slate-500 mb-4">
              {selectedCitation.page && <span>Page {selectedCitation.page}</span>}
              <span>Relevance: {(selectedCitation.relevance_score * 100).toFixed(1)}%</span>
              <span className="font-mono text-2xs text-slate-400">
                Chunk: {selectedCitation.chunk_id.slice(0, 8)}...
              </span>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-serif leading-relaxed text-slate-700 italic max-h-60 overflow-y-auto">
              "{selectedCitation.excerpt}"
            </div>
          </div>
        </div>
      )}

      {/* Retrieval Trace Modal */}
      {activeTrace && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-2xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl border border-slate-200 max-w-2xl w-full p-6 shadow-xl relative max-h-[85vh] overflow-y-auto">
            <button
              onClick={() => setActiveTrace(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1 rounded-md"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="flex items-center space-x-2 text-xs font-semibold text-blue-600 uppercase tracking-wider mb-2">
              <Sparkles className="w-4 h-4" />
              <span>Retrieval & Reasoning Trace</span>
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-4">
              How Aegis Answered This Query
            </h3>

            <div className="space-y-4 text-xs text-slate-700">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="font-semibold text-slate-900">Original Query:</span>{' '}
                {activeTrace.original_query}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="text-slate-500">Candidate Chunks Retrieved:</span>
                  <div className="text-base font-bold text-slate-900 mt-1">
                    {activeTrace.candidate_count}
                  </div>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="text-slate-500">Selected Evidence Chunks:</span>
                  <div className="text-base font-bold text-slate-900 mt-1">
                    {activeTrace.selected_evidence_count}
                  </div>
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-500">Grounding Coverage:</span>
                <div className="text-base font-bold text-emerald-600 mt-1">
                  {(activeTrace.grounding_coverage_pct * 100).toFixed(1)}%
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="font-semibold text-slate-900">Self-Correction:</span>{' '}
                {activeTrace.self_correction_triggered
                  ? `Triggered (${activeTrace.iterations} iterations)`
                  : 'Not required (First-pass grounding verified)'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

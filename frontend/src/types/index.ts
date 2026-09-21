export type NavigationTab = 'dashboard' | 'documents' | 'ask';

export interface HealthSubsystems {
  s3: {
    documents_bucket: string;
    configured: boolean;
  };
  dynamodb: {
    documents_table: string;
    conversations_table: string;
    evaluations_table: string;
    configured: boolean;
  };
  bedrock: {
    region: string;
    embedding_model: string;
    generation_model: string;
    configured: boolean;
  };
  opensearch: {
    endpoint_configured: boolean;
    index: string;
  };
  verification_engine: {
    grounding_threshold: number;
    max_self_correction_attempts: number;
    active: boolean;
  };
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'error';
  service: string;
  version: string;
  environment: string;
  region: string;
  timestamp: string;
  subsystems: HealthSubsystems;
}

export interface DashboardMetrics {
  documentsProcessed: number | null;
  totalChunks: number | null;
  indexedSources: number | null;
  totalQueries: number | null;
  avgRetrievalLatencyMs: number | null;
  avgGenerationLatencyMs: number | null;
  groundingRate: number | null;
  selfCorrectionRate: number | null;
  failedIngestionJobs: number | null;
}

export type ProcessingState =
  | 'UPLOADED'
  | 'PROCESSING'
  | 'EXTRACTING'
  | 'CHUNKING'
  | 'EMBEDDING'
  | 'INDEXING'
  | 'COMPLETED'
  | 'FAILED';

export interface DocumentItem {
  id: string;
  filename: string;
  fileType: 'pdf' | 'txt' | 'docx' | 'image' | 'csv';
  sizeBytes: number;
  uploadedAt: string;
  status: ProcessingState;
  chunkCount: number;
  extractionStatus: string;
  errorMessage?: string;
}

export interface Citation {
  document_id: string;
  filename: string;
  page?: number;
  section?: string;
  chunk_id: string;
  excerpt: string;
  relevance_score: number;
}

export interface ClaimVerification {
  claim_id: string;
  statement: string;
  is_grounded: boolean;
  citation_ids: string[];
}

export interface RetrievalTrace {
  query_id: string;
  timestamp: string;
  original_query: string;
  query_classification?: string;
  iterations: number;
  retrieval_strategies: string[];
  candidate_count: number;
  selected_evidence_count: number;
  grounding_coverage_pct: number;
  self_correction_triggered: boolean;
  latency_ms: {
    retrieval: number;
    generation: number;
    verification: number;
    total: number;
  };
}

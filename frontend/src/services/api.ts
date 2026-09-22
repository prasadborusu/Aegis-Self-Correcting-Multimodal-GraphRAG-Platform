import { HealthResponse, DashboardMetrics, DocumentItem } from '../types';

const API_BASE = '';

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`, {
    headers: { 'Accept': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch health status: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/metrics`);
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend metrics endpoint will be populated as queries & documents occur
  }

  return {
    documentsProcessed: null,
    totalChunks: null,
    indexedSources: null,
    totalQueries: null,
    avgRetrievalLatencyMs: null,
    avgGenerationLatencyMs: null,
    groundingRate: null,
    selfCorrectionRate: null,
    failedIngestionJobs: null,
  };
}

// Helper to normalize backend DocumentRecord to frontend DocumentItem
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapDocRecord(item: any): DocumentItem {
  return {
    id: item.document_id || item.id,
    filename: item.filename,
    fileType: (item.file_type || item.fileType || 'txt').toLowerCase(),
    sizeBytes: item.size_bytes !== undefined ? item.size_bytes : item.sizeBytes || 0,
    uploadedAt: item.uploaded_at || item.uploadedAt || new Date().toISOString(),
    status: item.status,
    chunkCount: item.chunk_count !== undefined ? item.chunk_count : item.chunkCount || 0,
    extractionStatus: item.extraction_status || item.extractionStatus || '',
    errorMessage: item.error_message || item.errorMessage,
  };
}

export async function fetchDocuments(): Promise<DocumentItem[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/documents`);
    if (res.ok) {
      const data = await res.json();
      return data.map(mapDocRecord);
    }
  } catch {
    // empty initially
  }
  return [];
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/v1/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let errorMsg = 'Failed to upload document';
    try {
      const errorData = await res.json();
      if (errorData.detail) errorMsg = errorData.detail;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  const data = await res.json();
  return mapDocRecord(data);
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!res.ok && res.status !== 404) {
    throw new Error(`Failed to delete document: ${res.statusText}`);
  }
}

export async function sendQuery(query: string, documentIds?: string[]) {
  const res = await fetch(`${API_BASE}/api/v1/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({
      query,
      document_ids: documentIds,
    }),
  });

  if (!res.ok) {
    let errorMsg = 'Failed to execute query';
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return await res.json();
}

export async function fetchConversationHistory(sessionId: string = 'default') {
  try {
    const res = await fetch(`${API_BASE}/api/v1/conversations?session_id=${encodeURIComponent(sessionId)}`);
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // fallback
  }
  return [];
}

export async function clearConversationHistory(sessionId: string = 'default'): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/conversations?session_id=${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
    return res.ok;
  } catch {
    return false;
  }
}


import React, { useState, useEffect, useRef } from 'react';
import {
  Upload,
  FileText,
  FileCode,
  Image as ImageIcon,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Trash2,
  XCircle,
} from 'lucide-react';
import { DocumentItem, ProcessingState } from '../types';
import { uploadDocument, deleteDocument } from '../services/api';

interface DocumentsPageProps {
  documents: DocumentItem[];
  onRefresh: () => void;
}

export const DocumentsPage: React.FC<DocumentsPageProps> = ({
  documents,
  onRefresh,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Poll faster (every 3s) if any document is actively processing
  const isProcessing = documents.some(
    (d) =>
      d.status !== 'COMPLETED' &&
      d.status !== 'FAILED' &&
      d.status !== undefined
  );

  useEffect(() => {
    if (!isProcessing) return;
    const timer = setInterval(() => {
      onRefresh();
    }, 3000);
    return () => clearInterval(timer);
  }, [isProcessing, onRefresh]);

  const handleFile = async (file: File) => {
    setErrorMessage(null);
    setUploading(true);
    try {
      await uploadDocument(file);
      onRefresh();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (docId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;
    try {
      await deleteDocument(docId);
      onRefresh();
    } catch (err: any) {
      alert(`Could not delete document: ${err.message}`);
    }
  };

  const getStatusBadge = (status: ProcessingState) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3" />
            <span>Ready</span>
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
            <AlertTriangle className="w-3 h-3" />
            <span>Failed</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <RefreshCw className="w-3 h-3 animate-spin" />
            <span>{status}</span>
          </span>
        );
    }
  };

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return <FileText className="w-5 h-5 text-red-500" />;
      case 'image':
      case 'png':
      case 'jpg':
      case 'jpeg':
        return <ImageIcon className="w-5 h-5 text-purple-500" />;
      default:
        return <FileCode className="w-5 h-5 text-slate-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Knowledge Sources</h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Upload and manage documents indexed into Aegis S3 and OpenSearch vector storage.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={onRefresh}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 transition-colors shadow-2xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin text-blue-600' : ''}`} />
            <span>Refresh Status</span>
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between text-xs text-red-700">
          <div className="flex items-center space-x-2">
            <XCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-red-500 hover:text-red-700 font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Upload Dropzone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragActive(false);
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
          }
        }}
        className={`border-2 border-dashed rounded-2xl p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50/50'
            : 'border-slate-300 hover:border-slate-400 bg-white'
        }`}
      >
        <div className="max-w-md mx-auto">
          <div className="w-12 h-12 mx-auto rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
            <Upload className={`w-6 h-6 ${uploading ? 'animate-bounce' : ''}`} />
          </div>
          <h3 className="text-sm font-semibold text-slate-800">
            {uploading ? 'Uploading to S3...' : 'Drag and drop your knowledge sources'}
          </h3>
          <p className="text-xs text-slate-500 mt-1 mb-4">
            Supported MVP formats: PDF, TXT, PNG, JPG (up to 25MB)
          </p>
          <label className="inline-flex items-center px-4 py-2 rounded-lg text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700 cursor-pointer transition-colors shadow-2xs">
            <span>{uploading ? 'Processing...' : 'Browse Files'}</span>
            <input
              ref={fileInputRef}
              type="file"
              disabled={uploading}
              className="hidden"
              accept=".pdf,.txt,.png,.jpg,.jpeg"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFile(e.target.files[0]);
                }
              }}
            />
          </label>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-900">
            Indexed Documents ({documents.length})
          </h2>
          <span className="text-xs text-slate-400 font-medium">
            Stored in S3 & OpenSearch Serverless
          </span>
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-16 px-4">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-700">No documents ingested yet</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Upload your PDF or text documents above to extract structure, generate embeddings,
              and build the searchable knowledge index.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 text-xs font-semibold text-slate-500 bg-slate-50/50">
                  <th className="py-3 px-6">Document</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Chunks</th>
                  <th className="py-3 px-4">Extraction</th>
                  <th className="py-3 px-4">Upload Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-6">
                      <div className="flex items-center space-x-3">
                        {getFileIcon(doc.fileType)}
                        <div>
                          <div className="font-semibold text-slate-900">{doc.filename}</div>
                          <div className="text-xs text-slate-400 font-mono">
                            {(doc.sizeBytes / 1024).toFixed(1)} KB
                          </div>
                          {doc.errorMessage && (
                            <div className="text-2xs text-red-600 font-medium mt-0.5">
                              Error: {doc.errorMessage}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 uppercase font-semibold text-slate-500">
                      {doc.fileType}
                    </td>
                    <td className="py-3.5 px-4">{getStatusBadge(doc.status)}</td>
                    <td className="py-3.5 px-4 font-mono font-medium text-slate-900">
                      {doc.chunkCount > 0 ? doc.chunkCount : '—'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 max-w-xs truncate">
                      {doc.extractionStatus}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {new Date(doc.uploadedAt).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        title="Delete Document"
                        onClick={() => handleDelete(doc.id, doc.filename)}
                        className="p-1.5 text-slate-400 hover:text-red-600 rounded-md hover:bg-red-50 transition-colors cursor-pointer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

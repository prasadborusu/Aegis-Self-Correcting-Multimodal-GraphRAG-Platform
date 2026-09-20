"""
Document, Chunk, and Citation Data Models for Aegis.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ProcessingState(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    EXTRACTING = "EXTRACTING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXING = "INDEXING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ChunkMetadata(BaseModel):
    document_id: str = Field(..., description="Parent document identifier")
    filename: str = Field(..., description="Original filename")
    page: Optional[int] = Field(None, description="1-indexed page number if available")
    section: Optional[str] = Field(None, description="Document section or header path")
    heading: Optional[str] = Field(None, description="Immediate heading context")
    chunk_index: int = Field(0, description="Sequential index within document")
    source_type: str = Field(..., description="Document source format (pdf, txt, image, etc.)")
    char_count: int = Field(0, description="Character length of chunk text")
    token_count: Optional[int] = Field(None, description="Estimated token count")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp of chunk generation",
    )


class Chunk(BaseModel):
    chunk_id: str = Field(..., description="Globally unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    text: str = Field(..., description="Normalized text content of the chunk")
    metadata: ChunkMetadata
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Dense vector embedding (e.g. 1024-dim for Titan v2)",
    )


class DocumentRecord(BaseModel):
    document_id: str = Field(..., description="Unique document UUID")
    filename: str = Field(..., description="Original uploaded filename")
    file_type: str = Field(..., description="Extension / format (pdf, txt, png, jpg)")
    size_bytes: int = Field(..., description="File size in bytes")
    s3_bucket: str = Field(..., description="S3 bucket storing original raw source")
    s3_key: str = Field(..., description="S3 object key")
    status: ProcessingState = Field(
        default=ProcessingState.UPLOADED,
        description="Current asynchronous processing state",
    )
    chunk_count: int = Field(0, description="Total chunks produced and indexed")
    extraction_status: str = Field(
        default="Pending",
        description="Status description of extraction phase",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Actionable diagnostic message if processing failed",
    )
    uploaded_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Upload timestamp",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last state transition timestamp",
    )
    extra_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional additional structural metadata",
    )


class Citation(BaseModel):
    document_id: str
    filename: str
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_id: str
    excerpt: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)

"""
Aegis Platform Configuration
All configurable parameters loaded from environment variables with safe defaults.
"""

from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Aegis - Self-Correcting Multimodal RAG"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", description="Environment name")
    log_level: str = Field(default="INFO", description="Logging level")

    # AWS General
    aws_region: str = Field(default="ap-south-1", description="AWS Deployment Region")

    # S3 Storage
    s3_bucket_documents: str = Field(
        default="aegis-knowledge-sources-dev",
        description="Bucket for raw uploaded knowledge sources",
    )
    s3_bucket_processed: str = Field(
        default="aegis-processed-artifacts-dev",
        description="Bucket for intermediate & processed artifacts",
    )

    # DynamoDB Tables
    dynamodb_documents_table: str = Field(
        default="aegis_documents_dev",
        description="Table for document metadata and processing state",
    )
    dynamodb_conversations_table: str = Field(
        default="aegis_conversations_dev",
        description="Table for query history, answers, and citation metadata",
    )
    dynamodb_evaluations_table: str = Field(
        default="aegis_evaluations_dev",
        description="Table for grounding evaluation and retrieval traces",
    )

    # Amazon Bedrock
    bedrock_region: str = Field(
        default="ap-south-1",
        description="Default region for Bedrock models",
    )
    bedrock_embedding_region: str = Field(
        default="us-east-1",
        description="Region where Bedrock embedding models are active",
    )
    bedrock_generation_region: str = Field(
        default="us-west-2",
        description="Region where Bedrock generation LLM models are active",
    )
    bedrock_embedding_model_id: str = Field(
        default="amazon.titan-embed-text-v2:0",
        description="Amazon Bedrock embedding model ID",
    )
    bedrock_generation_model_id: str = Field(
        default="amazon.nova-lite-v1:0",
        description="Amazon Bedrock primary generation LLM ID",
    )

    # Amazon OpenSearch Serverless
    opensearch_endpoint: str = Field(
        default="",
        description="Amazon OpenSearch Serverless collection endpoint URL",
    )
    opensearch_index: str = Field(
        default="aegis-knowledge-index",
        description="OpenSearch vector/hybrid index name",
    )
    opensearch_vector_field: str = Field(
        default="embedding",
        description="Vector field name in index mapping",
    )
    opensearch_vector_dimension: int = Field(
        default=1024,
        description="Dimension of embeddings (e.g. 1024 for Titan v2)",
    )

    # Chunking
    chunk_size: int = Field(
        default=800,
        description="Target chunk size in characters/tokens",
    )
    chunk_overlap: int = Field(
        default=150,
        description="Overlap between consecutive chunks",
    )

    # Retrieval & Reranking
    retrieval_top_k: int = Field(
        default=20,
        description="Number of candidate chunks retrieved before reranking",
    )
    reranking_top_k: int = Field(
        default=8,
        description="Number of chunks kept after reranking for LLM prompt context",
    )

    # Grounding & Verification
    grounding_threshold: float = Field(
        default=0.75,
        description="Minimum grounding coverage ratio to accept answer without correction",
    )
    max_self_correction_attempts: int = Field(
        default=3,
        description="Strict safety ceiling for self-correcting query rewrites",
    )

    # API Server
    api_host: str = Field(default="0.0.0.0", description="FastAPI host bind")
    api_port: int = Field(default=8000, description="FastAPI port")
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        description="Allowed CORS origin URLs",
    )


@lru_cache()
def get_settings() -> Settings:
    """Returns singleton settings instance cached across calls."""
    return Settings()

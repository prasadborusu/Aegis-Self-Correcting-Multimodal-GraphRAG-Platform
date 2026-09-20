from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'Aegis'
    app_version: str = '0.1.0'
    aws_region: str = 'ap-south-1'
    s3_bucket_documents: str = 'aegis-knowledge-sources-dev'
    s3_bucket_processed: str = 'aegis-processed-artifacts-dev'
    dynamodb_documents_table: str = 'aegis_documents_dev'
    dynamodb_conversations_table: str = 'aegis_conversations_dev'
    bedrock_region: str = 'ap-south-1'
    bedrock_embedding_region: str = 'us-east-1'
    bedrock_generation_region: str = 'us-west-2'
    bedrock_embedding_model_id: str = 'amazon.titan-embed-text-v2:0'
    bedrock_generation_model_id: str = 'amazon.nova-lite-v1:0'
    opensearch_endpoint: str = ''
    opensearch_index: str = 'aegis-knowledge-index'
    opensearch_vector_dimension: int = 1024
    chunk_size: int = 800
    chunk_overlap: int = 150
    retrieval_top_k: int = 20
    reranking_top_k: int = 8
    grounding_threshold: float = 0.75
    max_self_correction_attempts: int = 3

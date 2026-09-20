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

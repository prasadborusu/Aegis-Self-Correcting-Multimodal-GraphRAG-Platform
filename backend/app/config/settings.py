from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'Aegis'
    app_version: str = '0.1.0'
    aws_region: str = 'ap-south-1'
    s3_bucket_documents: str = 'aegis-knowledge-sources-dev'
    s3_bucket_processed: str = 'aegis-processed-artifacts-dev'
    dynamodb_documents_table: str = 'aegis_documents_dev'
    dynamodb_conversations_table: str = 'aegis_conversations_dev'

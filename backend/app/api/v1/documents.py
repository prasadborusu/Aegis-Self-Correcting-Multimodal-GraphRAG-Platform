"""
Document Ingestion & Management API Endpoints for Aegis.
"""

import uuid
import logging
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status, Depends

from backend.app.config.settings import Settings, get_settings
from backend.app.models.document import DocumentRecord, ProcessingState
from backend.app.services.s3_storage import S3StorageService
from backend.app.services.dynamo_db import DynamoDBMetadataService
from backend.app.ingestion.pipeline import IngestionPipeline

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger("aegis.api.documents")

s3_service = S3StorageService()
dynamo_service = DynamoDBMetadataService()
pipeline = IngestionPipeline(s3_service=s3_service, dynamo_service=dynamo_service)


@router.post("/upload", response_model=DocumentRecord, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    """
    Asynchronous non-blocking document upload endpoint.
    Uploads raw file to S3, initializes DynamoDB tracking record, and schedules background processing.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    content = await file.read()
    filename = file.filename

    # Validate file
    is_valid, error_msg = s3_service.validate_file(filename, content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    document_id = str(uuid.uuid4())
    file_type = Path(filename).suffix.lstrip(".").lower()

    # Upload to S3
    try:
        s3_bucket, s3_key = await s3_service.upload_document(
            document_id=document_id,
            filename=filename,
            content=content,
            content_type=file.content_type or "application/octet-stream",
        )
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to persist document to storage")

    # Initialize DynamoDB Record
    record = DocumentRecord(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        size_bytes=len(content),
        s3_bucket=s3_bucket,
        s3_key=s3_key,
        status=ProcessingState.UPLOADED,
        extraction_status="File uploaded; queued for asynchronous processing",
    )
    await dynamo_service.save_document(record)

    # Launch background processing task (non-blocking)
    background_tasks.add_task(
        pipeline.run_pipeline,
        document_id=document_id,
        filename=filename,
        content=content,
        file_type=file_type,
    )

    return record


@router.get("", response_model=List[DocumentRecord])
async def list_documents():
    """
    List all ingested documents and their current processing status.
    """
    return await dynamo_service.list_documents()


@router.get("/{document_id}", response_model=DocumentRecord)
async def get_document(document_id: str):
    """
    Retrieve document processing state and metadata.
    """
    doc = await dynamo_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    """
    Delete document and all associated chunks.
    """
    doc = await dynamo_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    s3_service.delete_document(document_id, doc.filename, doc.s3_key)
    await dynamo_service.delete_document(document_id)
    return None

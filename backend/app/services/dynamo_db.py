"""
DynamoDB Metadata Service for Aegis.
Manages document processing lifecycle states and query history with local persistent fallback.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError

from backend.app.config.settings import Settings, get_settings
from backend.app.models.document import DocumentRecord, ProcessingState

logger = logging.getLogger("aegis.dynamodb")


class DynamoDBMetadataService:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.table_name = self.settings.dynamodb_documents_table
        self.region = self.settings.aws_region

        # Local fallback store for offline tests and development
        self.local_metadata_file = Path("./.storage/metadata/documents.json")
        self.local_metadata_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.local_metadata_file.exists():
            self.local_metadata_file.write_text("{}", encoding="utf-8")

        self._dynamodb_resource = None

    @property
    def dynamodb(self):
        if self._dynamodb_resource is None:
            self._dynamodb_resource = boto3.resource("dynamodb", region_name=self.region)
        return self._dynamodb_resource

    def _read_local_docs(self) -> dict:
        try:
            return json.loads(self.local_metadata_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_local_docs(self, data: dict) -> None:
        self.local_metadata_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    async def save_document(self, record: DocumentRecord) -> DocumentRecord:
        """
        Create or update a document record in DynamoDB and local store.
        """
        record.updated_at = datetime.now(timezone.utc).isoformat()
        item = record.model_dump()

        # Update local store
        local_data = self._read_local_docs()
        local_data[record.document_id] = item
        self._write_local_docs(local_data)

        # Sync with AWS DynamoDB if table exists
        try:
            table = self.dynamodb.Table(self.table_name)
            table.put_item(Item=item)
            logger.info(f"Saved doc {record.document_id} ({record.filename}) to DynamoDB table {self.table_name}")
        except ClientError as e:
            logger.warning(
                f"DynamoDB put_item to {self.table_name} skipped/failed ({e.response.get('Error', {}).get('Code')}); "
                f"using local metadata store"
            )

        return record

    async def update_status(
        self,
        document_id: str,
        status: ProcessingState,
        extraction_status: str,
        chunk_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[DocumentRecord]:
        """
        Update the processing state machine for a document.
        """
        doc = await self.get_document(document_id)
        if not doc:
            return None

        doc.status = status
        doc.extraction_status = extraction_status
        if chunk_count is not None:
            doc.chunk_count = chunk_count
        if error_message is not None:
            doc.error_message = error_message
        doc.updated_at = datetime.now(timezone.utc).isoformat()

        return await self.save_document(doc)

    async def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        """
        Retrieve document metadata by document_id.
        """
        # Check local store first
        local_data = self._read_local_docs()
        if document_id in local_data:
            return DocumentRecord(**local_data[document_id])

        # Query DynamoDB
        try:
            table = self.dynamodb.Table(self.table_name)
            resp = table.get_item(Key={"document_id": document_id})
            if "Item" in resp:
                item = resp["Item"]
                # Cache locally
                local_data[document_id] = item
                self._write_local_docs(local_data)
                return DocumentRecord(**item)
        except Exception as e:
            logger.warning(f"DynamoDB get_item error: {e}")

        return None

    async def list_documents(self) -> List[DocumentRecord]:
        """
        List all ingested document records.
        """
        records: List[DocumentRecord] = []

        # From local cache
        local_data = self._read_local_docs()
        for item in local_data.values():
            records.append(DocumentRecord(**item))

        # Sort by uploaded_at descending
        records.sort(key=lambda d: d.uploaded_at, reverse=True)
        return records

    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document record from metadata store.
        """
        local_data = self._read_local_docs()
        if document_id in local_data:
            del local_data[document_id]
            self._write_local_docs(local_data)

        try:
            table = self.dynamodb.Table(self.table_name)
            table.delete_item(Key={"document_id": document_id})
            return True
        except Exception as e:
            logger.warning(f"DynamoDB delete_item error: {e}")
            return True

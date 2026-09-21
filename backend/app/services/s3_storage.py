"""
S3 Storage Service for Aegis.
Handles secure upload, validation, and retrieval of raw documents and processed artifacts.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
import boto3
from botocore.exceptions import ClientError

from backend.app.config.settings import Settings, get_settings

logger = logging.getLogger("aegis.s3")

# 25 MB limit for MVP
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg"}


class S3StorageService:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.bucket_documents = self.settings.s3_bucket_documents
        self.bucket_processed = self.settings.s3_bucket_processed
        self.region = self.settings.aws_region

        # Local storage fallback directory for persistent cache/testing
        self.local_base_dir = Path("./.storage")
        self.local_base_dir.mkdir(parents=True, exist_ok=True)

        self._s3_client = None

    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client("s3", region_name=self.region)
        return self._s3_client

    def validate_file(self, filename: str, content: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate file extension, size, and header magic numbers.
        """
        if len(content) == 0:
            return False, "File is empty"

        if len(content) > MAX_FILE_SIZE_BYTES:
            return False, f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB"

        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file extension '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"

        # Magic bytes validation
        if ext == ".pdf":
            if not content.startswith(b"%PDF-"):
                return False, "Invalid PDF: Missing %PDF- file header"
        elif ext == ".png":
            if not content.startswith(b"\x89PNG\r\n\x1a\n"):
                return False, "Invalid PNG: Missing PNG file signature"
        elif ext in {".jpg", ".jpeg"}:
            if not content.startswith(b"\xff\xd8\xff"):
                return False, "Invalid JPEG: Missing JPEG SOI marker"
        elif ext == ".txt":
            try:
                content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    content.decode("latin-1")
                except Exception:
                    return False, "Text file is not valid UTF-8 or Latin-1 encoded"

        return True, None

    async def upload_document(
        self,
        document_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> Tuple[str, str]:
        """
        Upload raw document content to S3 raw bucket.
        Returns (s3_bucket, s3_key).
        """
        s3_key = f"raw/{document_id}/{filename}"

        # Always save to local cache for resilient offline processing & extraction
        local_path = self.local_base_dir / "documents" / document_id / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(content)

        # Upload to AWS S3 if accessible
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_documents,
                Key=s3_key,
                Body=content,
                ContentType=content_type,
                Metadata={
                    "document_id": document_id,
                    "filename": filename,
                },
            )
            logger.info(f"Uploaded {filename} ({len(content)} bytes) to s3://{self.bucket_documents}/{s3_key}")
        except ClientError as e:
            logger.warning(
                f"S3 upload to bucket {self.bucket_documents} skipped/failed ({e.response.get('Error', {}).get('Code')}); "
                f"retained in local store {local_path}"
            )

        return self.bucket_documents, s3_key

    def get_document_content(self, document_id: str, filename: str, s3_key: str) -> bytes:
        """
        Fetch document bytes from local store or S3.
        """
        local_path = self.local_base_dir / "documents" / document_id / filename
        if local_path.exists():
            return local_path.read_bytes()

        # Fallback to S3
        resp = self.s3_client.get_object(Bucket=self.bucket_documents, Key=s3_key)
        content = resp["Body"].read()
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(content)
        return content

    def delete_document(self, document_id: str, filename: str, s3_key: str) -> None:
        """
        Remove document from S3 and local storage.
        """
        local_path = self.local_base_dir / "documents" / document_id / filename
        if local_path.exists():
            local_path.unlink()

        try:
            self.s3_client.delete_object(Bucket=self.bucket_documents, Key=s3_key)
        except Exception as e:
            logger.warning(f"Could not delete from S3 ({s3_key}): {e}")

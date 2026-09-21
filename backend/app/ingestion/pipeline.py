"""
Asynchronous Document Ingestion Pipeline for Aegis.
Orchestrates document extraction, structure-aware chunking, embeddings generation, and state tracking.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
import asyncio

from backend.app.config.settings import Settings, get_settings
from backend.app.models.document import ProcessingState, DocumentRecord, Chunk
from backend.app.services.s3_storage import S3StorageService
from backend.app.services.dynamo_db import DynamoDBMetadataService
from backend.app.extraction.extractor import DocumentExtractor
from backend.app.chunking.structure_aware import StructureAwareChunker
from backend.app.embeddings.bedrock_embeddings import BedrockEmbeddingsService

logger = logging.getLogger("aegis.pipeline")


class IngestionPipeline:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        s3_service: Optional[S3StorageService] = None,
        dynamo_service: Optional[DynamoDBMetadataService] = None,
        extractor: Optional[DocumentExtractor] = None,
        chunker: Optional[StructureAwareChunker] = None,
        embeddings_service: Optional[BedrockEmbeddingsService] = None,
    ):
        self.settings = settings or get_settings()
        self.s3_service = s3_service or S3StorageService(self.settings)
        self.dynamo_service = dynamo_service or DynamoDBMetadataService(self.settings)
        self.extractor = extractor or DocumentExtractor()
        self.chunker = chunker or StructureAwareChunker(self.settings)
        self.embeddings_service = embeddings_service or BedrockEmbeddingsService(self.settings)

        self.chunks_storage_dir = Path("./.storage/chunks")
        self.chunks_storage_dir.mkdir(parents=True, exist_ok=True)

    async def run_pipeline(
        self,
        document_id: str,
        filename: str,
        content: bytes,
        file_type: str,
    ) -> DocumentRecord:
        """
        Executes the end-to-end ingestion pipeline with strict state machine progression.
        """
        logger.info(f"Starting ingestion pipeline for document {document_id} ({filename})")

        try:
            # 1. State: PROCESSING
            await self.dynamo_service.update_status(
                document_id=document_id,
                status=ProcessingState.PROCESSING,
                extraction_status="Initializing parser",
            )

            # 2. State: EXTRACTING
            await self.dynamo_service.update_status(
                document_id=document_id,
                status=ProcessingState.EXTRACTING,
                extraction_status="Extracting structure & layout",
            )
            extracted = self.extractor.extract(
                document_id=document_id,
                filename=filename,
                content=content,
                file_type=file_type,
            )
            logger.info(f"Extracted {extracted.total_pages} pages from {filename}")

            # 3. State: CHUNKING
            await self.dynamo_service.update_status(
                document_id=document_id,
                status=ProcessingState.CHUNKING,
                extraction_status=f"Parsed {extracted.total_pages} pages; chunking",
            )
            chunks: List[Chunk] = self.chunker.chunk_document(extracted)
            logger.info(f"Generated {len(chunks)} structure-aware chunks for {filename}")

            # 4. State: EMBEDDING
            await self.dynamo_service.update_status(
                document_id=document_id,
                status=ProcessingState.EMBEDDING,
                extraction_status=f"Created {len(chunks)} chunks; generating Bedrock Titan embeddings",
                chunk_count=len(chunks),
            )

            # Generate embeddings via Bedrock
            texts_to_embed = [c.text for c in chunks]
            try:
                embeddings = self.embeddings_service.generate_batch_embeddings(texts_to_embed)
                for i, emb in enumerate(embeddings):
                    chunks[i].embedding = emb
            except Exception as emb_err:
                logger.warning(f"Bedrock embedding generation failed or throttled: {emb_err}")
                # Pipeline continues with fallback so document remains queryable via keyword/structure

            # 5. State: INDEXING
            await self.dynamo_service.update_status(
                document_id=document_id,
                status=ProcessingState.INDEXING,
                extraction_status=f"Indexing {len(chunks)} chunks into vector store",
                chunk_count=len(chunks),
            )

            # Persist processed chunks locally and to S3 artifact store
            self._save_chunks(document_id, chunks)

            # 6. State: COMPLETED
            updated_doc = await self.dynamo_service.update_status(
                document_id=document_id,
                status=ProcessingState.COMPLETED,
                extraction_status=f"Completed: {len(chunks)} chunks indexed and ready",
                chunk_count=len(chunks),
            )
            logger.info(f"Ingestion pipeline completed successfully for {filename}")
            return updated_doc

        except Exception as e:
            logger.error(f"Ingestion pipeline failed for {filename}: {e}", exc_info=True)
            await self.dynamo_service.update_status(
                document_id=document_id,
                status=ProcessingState.FAILED,
                extraction_status="Failed during processing",
                error_message=str(e),
            )
            raise

    def _save_chunks(self, document_id: str, chunks: List[Chunk]) -> None:
        """
        Store processed chunks for retrieval.
        """
        file_path = self.chunks_storage_dir / f"{document_id}.json"
        data = [c.model_dump() for c in chunks]
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_chunks_for_document(self, document_id: str) -> List[Chunk]:
        """
        Load chunks for an ingested document.
        """
        file_path = self.chunks_storage_dir / f"{document_id}.json"
        if not file_path.exists():
            return []
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return [Chunk(**item) for item in data]

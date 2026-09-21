"""
Structure-Aware Document Chunker for Aegis.
Splits documents on natural paragraph and heading boundaries while preserving page and provenance metadata.
"""

import uuid
import re
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.models.document import Chunk, ChunkMetadata
from backend.app.extraction.extractor import ExtractedDocument, ExtractedPage
from backend.app.config.settings import Settings, get_settings


class StructureAwareChunker:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.chunk_size = self.settings.chunk_size
        self.chunk_overlap = self.settings.chunk_overlap

    def chunk_document(self, extracted: ExtractedDocument) -> List[Chunk]:
        """
        Produce structure-aware chunks across all pages of an extracted document.
        """
        all_chunks: List[Chunk] = []
        global_chunk_idx = 0

        for page in extracted.pages:
            page_chunks = self._chunk_page(
                page=page,
                document_id=extracted.document_id,
                filename=extracted.filename,
                source_type=extracted.file_type,
                start_index=global_chunk_idx,
            )
            all_chunks.extend(page_chunks)
            global_chunk_idx += len(page_chunks)

        return all_chunks

    def _chunk_page(
        self,
        page: ExtractedPage,
        document_id: str,
        filename: str,
        source_type: str,
        start_index: int,
    ) -> List[Chunk]:
        text = page.text.strip()
        if not text:
            return []

        # Split into structural blocks: double newlines or heading boundaries
        blocks = self._split_into_blocks(text)
        page_chunks: List[Chunk] = []

        current_text = ""
        current_heading: Optional[str] = page.headings[0] if page.headings else None
        current_section: Optional[str] = None
        chunk_idx = start_index

        for block in blocks:
            is_new_heading = self._is_heading(block)

            # Finalize previous chunk if adding block exceeds chunk_size OR if a new heading starts
            if len(current_text) > 0 and (is_new_heading or len(current_text) + len(block) > self.chunk_size):
                chunk_id = f"{document_id}#p{page.page_number}_c{chunk_idx}"
                metadata = ChunkMetadata(
                    document_id=document_id,
                    filename=filename,
                    page=page.page_number,
                    section=current_section,
                    heading=current_heading,
                    chunk_index=chunk_idx,
                    source_type=source_type,
                    char_count=len(current_text.strip()),
                    token_count=len(current_text.split()),
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                page_chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        text=current_text.strip(),
                        metadata=metadata,
                    )
                )
                chunk_idx += 1

                # If splitting on a new heading, start fresh without dragging unrelated text into the new heading
                overlap_text = "" if is_new_heading else (
                    current_text[-self.chunk_overlap :] if len(current_text) > self.chunk_overlap else ""
                )
                current_text = overlap_text + "\n\n" + block if overlap_text else block

                if is_new_heading:
                    current_heading = block.strip("#").strip()
                    current_section = current_heading
            else:
                if is_new_heading:
                    current_heading = block.strip("#").strip()
                    current_section = current_heading

                if current_text:
                    current_text += "\n\n" + block
                else:
                    current_text = block

        # Add remaining text as the final chunk for this page
        if current_text.strip():
            chunk_id = f"{document_id}#p{page.page_number}_c{chunk_idx}"
            metadata = ChunkMetadata(
                document_id=document_id,
                filename=filename,
                page=page.page_number,
                section=current_section,
                heading=current_heading,
                chunk_index=chunk_idx,
                source_type=source_type,
                char_count=len(current_text.strip()),
                token_count=len(current_text.split()),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            page_chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    text=current_text.strip(),
                    metadata=metadata,
                )
            )

        return page_chunks

    def _split_into_blocks(self, text: str) -> List[str]:
        """
        Split text into paragraphs and structural blocks.
        """
        raw_blocks = re.split(r"\n\s*\n", text)
        clean_blocks = []
        for b in raw_blocks:
            cleaned = b.strip()
            if cleaned:
                # If a single block is excessively long (e.g. unformatted OCR dump), split by sentences
                if len(cleaned) > self.chunk_size * 1.5:
                    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
                    sentence_buf = ""
                    for s in sentences:
                        if len(sentence_buf) + len(s) > self.chunk_size and sentence_buf:
                            clean_blocks.append(sentence_buf.strip())
                            sentence_buf = s
                        else:
                            sentence_buf += (" " if sentence_buf else "") + s
                    if sentence_buf.strip():
                        clean_blocks.append(sentence_buf.strip())
                else:
                    clean_blocks.append(cleaned)
        return clean_blocks

    def _is_heading(self, text: str) -> bool:
        trimmed = text.strip()
        if trimmed.startswith("#"):
            return True
        if re.match(r"^\d+(\.\d+)*\s+[A-Z]", trimmed):
            return True
        if trimmed.isupper() and 3 < len(trimmed) < 60:
            return True
        return False

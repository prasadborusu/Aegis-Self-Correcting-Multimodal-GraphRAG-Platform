"""
Citation Extraction and Verification Engine for Aegis.
Extracts grounded citations from model answers and maps them to verified chunk evidence.
"""

import re
import logging
from typing import List, Tuple, Dict
from backend.app.models.document import Chunk, Citation

logger = logging.getLogger("aegis.citations")


class CitationGenerator:
    def extract_citations(
        self,
        answer: str,
        retrieved_evidence: List[Tuple[Chunk, float]],
    ) -> List[Citation]:
        """
        Scan answer for chunk citations [Chunk: <chunk_id>] and map them to verified evidence chunks.
        """
        # Map chunks by chunk_id
        chunk_map: Dict[str, Tuple[Chunk, float]] = {
            chunk.chunk_id: (chunk, score) for chunk, score in retrieved_evidence
        }

        # Regex to detect bracketed chunk citations, e.g. [Chunk: doc#p1_c0]
        cited_ids = re.findall(r"\[Chunk:\s*([^\]]+)\]", answer)

        citations: List[Citation] = []
        seen_chunks = set()

        for cid in cited_ids:
            clean_cid = cid.strip()
            if clean_cid in chunk_map and clean_cid not in seen_chunks:
                chunk, score = chunk_map[clean_cid]
                # Extract excerpt from chunk text (first 200 chars or summary)
                excerpt = chunk.text[:220].strip()
                if len(chunk.text) > 220:
                    excerpt += "..."

                citations.append(
                    Citation(
                        document_id=chunk.document_id,
                        filename=chunk.metadata.filename,
                        page=chunk.metadata.page,
                        section=chunk.metadata.section,
                        chunk_id=chunk.chunk_id,
                        excerpt=excerpt,
                        relevance_score=score,
                    )
                )
                seen_chunks.add(clean_cid)

        # If LLM cited evidence indirectly without explicit tags, include top relevant chunks as verified sources
        if not citations and retrieved_evidence and "insufficient evidence" not in answer.lower():
            for chunk, score in retrieved_evidence[:3]:
                if chunk.chunk_id not in seen_chunks:
                    excerpt = chunk.text[:220].strip()
                    if len(chunk.text) > 220:
                        excerpt += "..."
                    citations.append(
                        Citation(
                            document_id=chunk.document_id,
                            filename=chunk.metadata.filename,
                            page=chunk.metadata.page,
                            section=chunk.metadata.section,
                            chunk_id=chunk.chunk_id,
                            excerpt=excerpt,
                            relevance_score=score,
                        )
                    )
                    seen_chunks.add(chunk.chunk_id)

        return citations

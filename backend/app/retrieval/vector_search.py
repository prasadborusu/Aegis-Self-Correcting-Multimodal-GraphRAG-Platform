"""
Vector & Hybrid Retrieval Engine for Aegis.
Performs dense semantic vector similarity search and keyword matching over document chunks.
"""

import math
import logging
import re
from typing import List, Tuple, Optional
from backend.app.models.document import Chunk
from backend.app.embeddings.bedrock_embeddings import BedrockEmbeddingsService
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.config.settings import Settings, get_settings

logger = logging.getLogger("aegis.retrieval")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two normalized vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot_product / (norm_a * norm_b)))


class VectorSearchRetriever:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        embeddings_service: Optional[BedrockEmbeddingsService] = None,
        pipeline: Optional[IngestionPipeline] = None,
    ):
        self.settings = settings or get_settings()
        self.embeddings_service = embeddings_service or BedrockEmbeddingsService(self.settings)
        self.pipeline = pipeline or IngestionPipeline(self.settings)
        self.top_k = self.settings.retrieval_top_k

    def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: Optional[int] = None,
    ) -> List[Tuple[Chunk, float]]:
        """
        Embed the user query and retrieve top-k most relevant chunks ranked by cosine similarity and keyword overlap.
        """
        k = top_k or self.top_k

        # 1. Generate query embedding using Bedrock Titan v2
        query_embedding: Optional[List[float]] = None
        try:
            query_embedding = self.embeddings_service.generate_embedding(query)
        except Exception as e:
            logger.info(f"Bedrock vector embedding offline, proceeding with keyword and lexical semantic scoring: {e}")

        # 2. Gather candidate chunks across specified or all ingested documents
        all_chunks: List[Chunk] = []
        if document_ids:
            for doc_id in document_ids:
                all_chunks.extend(self.pipeline.get_chunks_for_document(doc_id))
        else:
            # Load chunks across all stored documents
            chunk_files = list(self.pipeline.chunks_storage_dir.glob("*.json"))
            for cf in chunk_files:
                doc_id = cf.stem
                all_chunks.extend(self.pipeline.get_chunks_for_document(doc_id))

        if not all_chunks:
            logger.info("No chunks available in storage for retrieval.")
            return []

        # 3. Score candidates
        scored_candidates: List[Tuple[Chunk, float]] = []
        raw_query_terms = set(re.findall(r"\w+", query.lower()))
        stopwords = {"a", "an", "the", "in", "on", "of", "and", "or", "to", "is", "are", "what", "does", "about", "for", "with", "this", "that"}
        query_terms = {t for t in raw_query_terms if t not in stopwords} or raw_query_terms

        for chunk in all_chunks:
            score = 0.0
            # Semantic vector score
            if query_embedding and chunk.embedding:
                vector_sim = cosine_similarity(query_embedding, chunk.embedding)
                score += vector_sim * 0.8

            # Keyword lexical score
            chunk_words = set(re.findall(r"\w+", chunk.text.lower()))
            if query_terms:
                keyword_overlap = len(query_terms.intersection(chunk_words)) / len(query_terms)
                lexical_weight = 0.2 if (query_embedding and chunk.embedding) else 1.0
                score += keyword_overlap * lexical_weight

            if score > 0.05:
                scored_candidates.append((chunk, round(score, 4)))

        # 4. Sort descending by relevance score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:k]

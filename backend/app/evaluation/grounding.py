"""
Claim-Level Grounding Evaluator for Aegis.
Extracts factual claims from answers and calculates grounding coverage against evidence chunks.
"""

import re
import logging
from typing import List, Tuple, Dict, Any
from pydantic import BaseModel
from backend.app.models.document import Chunk

logger = logging.getLogger("aegis.evaluation")


class ClaimResult(BaseModel):
    claim_id: str
    statement: str
    is_grounded: bool
    supporting_chunk_ids: List[str]
    confidence: float


class GroundingEvaluation(BaseModel):
    total_claims: int
    supported_claims: int
    grounding_coverage: float
    claims: List[ClaimResult]
    is_sufficient: bool


class ClaimGroundingEvaluator:
    def __init__(self, threshold: float = 0.75):
        self.threshold = threshold

    def evaluate(
        self,
        answer: str,
        evidence_chunks: List[Tuple[Chunk, float]],
    ) -> GroundingEvaluation:
        """
        Decomposes answer into atomic claims, verifies each against evidence, and computes grounding score.
        """
        # If the answer explicitly declares insufficient evidence, return 100% truthful grounded coverage
        if "couldn't find sufficient evidence" in answer.lower() or "insufficient evidence" in answer.lower():
            return GroundingEvaluation(
                total_claims=1,
                supported_claims=1,
                grounding_coverage=1.0,
                claims=[
                    ClaimResult(
                        claim_id="claim_0",
                        statement="Evidence is insufficient to answer the query.",
                        is_grounded=True,
                        supporting_chunk_ids=[],
                        confidence=1.0,
                    )
                ],
                is_sufficient=True,
            )

        # 1. Segment answer into sentences/claims
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if len(s.strip()) > 15]

        if not sentences:
            return GroundingEvaluation(
                total_claims=0,
                supported_claims=0,
                grounding_coverage=1.0,
                claims=[],
                is_sufficient=True,
            )

        claim_results: List[ClaimResult] = []
        supported_count = 0

        # Combine all evidence text for quick lexical verification
        evidence_corpus = " ".join([c.text.lower() for c, _ in evidence_chunks])

        for i, sentence in enumerate(sentences):
            clean_sentence = re.sub(r"\[Chunk:\s*[^\]]+\]", "", sentence).strip()
            sentence_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", clean_sentence.lower()))

            # Check matching chunks
            matching_chunks = []
            for chunk, score in evidence_chunks:
                chunk_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", chunk.text.lower()))
                if sentence_words:
                    overlap_ratio = len(sentence_words.intersection(chunk_words)) / len(sentence_words)
                    if overlap_ratio >= 0.40:
                        matching_chunks.append(chunk.chunk_id)

            is_grounded = len(matching_chunks) > 0
            confidence = min(1.0, 0.5 + (0.1 * len(matching_chunks))) if is_grounded else 0.2

            if is_grounded:
                supported_count += 1

            claim_results.append(
                ClaimResult(
                    claim_id=f"claim_{i+1}",
                    statement=clean_sentence,
                    is_grounded=is_grounded,
                    supporting_chunk_ids=matching_chunks,
                    confidence=round(confidence, 2),
                )
            )

        total_claims = len(sentences)
        coverage = round(supported_count / total_claims, 4) if total_claims > 0 else 1.0
        is_sufficient = coverage >= self.threshold

        return GroundingEvaluation(
            total_claims=total_claims,
            supported_claims=supported_count,
            grounding_coverage=coverage,
            claims=claim_results,
            is_sufficient=is_sufficient,
        )

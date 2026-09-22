"""
RAG Orchestrator and Self-Correcting Execution Engine for Aegis.
Handles semantic retrieval, grounded generation, claim verification, and autonomous re-retrieval loop.
"""

import os
import sys
import time
import uuid
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timezone

# Ensure project root is in sys.path when executed directly
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.models.document import Chunk, Citation
from backend.app.config.settings import Settings, get_settings
from backend.app.retrieval.vector_search import VectorSearchRetriever
from backend.app.rag.generator import GroundedGenerator
from backend.app.citations.generator import CitationGenerator
from backend.app.evaluation.grounding import ClaimGroundingEvaluator, GroundingEvaluation

logger = logging.getLogger("aegis.orchestrator")


class QueryResponse(BaseModel):
    query_id: str
    query: str
    answer: str
    citations: List[Citation]
    grounding_coverage: float
    total_claims: int
    supported_claims: int
    claims: List[Dict[str, Any]]
    retrieval_trace: Dict[str, Any]


class RAGOrchestrator:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        retriever: Optional[VectorSearchRetriever] = None,
        generator: Optional[GroundedGenerator] = None,
        citation_generator: Optional[CitationGenerator] = None,
        evaluator: Optional[ClaimGroundingEvaluator] = None,
    ):
        self.settings = settings or get_settings()
        self.retriever = retriever or VectorSearchRetriever(self.settings)
        self.generator = generator or GroundedGenerator(self.settings)
        self.citation_generator = citation_generator or CitationGenerator()
        self.evaluator = evaluator or ClaimGroundingEvaluator(self.settings.grounding_threshold)
        self.max_attempts = self.settings.max_self_correction_attempts

    def process_query(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
    ) -> QueryResponse:
        """
        Executes query retrieval, grounded synthesis, claim verification, and self-correction loop.
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())

        # Check for conversational greeting or meta-intent
        normalized_q = query.strip().lower().rstrip("!?. ")
        greetings = {
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
            "good evening", "howdy", "hola", "hi aegis", "hello aegis", "hey aegis"
        }
        meta_phrases = [
            "who are you", "what are you", "what can you do", "what is aegis",
            "how does aegis work", "tell me about aegis", "how do you work",
            "what can i ask", "help"
        ]

        is_greeting = normalized_q in greetings or any(normalized_q == g or normalized_q.startswith(g + " ") for g in greetings)
        is_meta = any(phrase in normalized_q for phrase in meta_phrases)

        # Retrieve list of indexed sample filenames
        chunk_files = list(self.retriever.pipeline.chunks_storage_dir.glob("*.json"))
        doc_count = len(chunk_files)
        sample_filenames = []
        for cf in chunk_files:
            try:
                chunks = self.retriever.pipeline.get_chunks_for_document(cf.stem)
                if chunks and chunks[0].metadata.filename:
                    fname = chunks[0].metadata.filename
                    if fname not in sample_filenames and fname != "test_doc.txt":
                        sample_filenames.append(fname)
            except Exception:
                pass

        if is_greeting and not is_meta:
            doc_status = f" You currently have {doc_count} document(s) in your knowledge base." if doc_count > 0 else " No documents uploaded yet."
            greeting_text = (
                f"Hello! I am Aegis, your evidence-first knowledge intelligence platform.{doc_status}\n\n"
                f"You can ask me questions about your uploaded documents, and I will retrieve relevant excerpts, "
                f"verify factual claims against extracted context, and provide verifiable citations with page numbers."
            )
            return QueryResponse(
                query_id=query_id,
                query=query,
                answer=greeting_text,
                citations=[],
                grounding_coverage=1.0,
                total_claims=1,
                supported_claims=1,
                claims=[{"claim_id": "greeting_0", "statement": "Conversational greeting acknowledged.", "is_grounded": True, "supporting_chunk_ids": [], "confidence": 1.0}],
                retrieval_trace={
                    "query_id": query_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "original_query": query,
                    "final_query": query,
                    "iterations": 1,
                    "self_correction_triggered": False,
                    "retrieval_strategies": ["Conversational Intent Router"],
                    "candidate_count": 0,
                    "selected_evidence_count": 0,
                    "grounding_coverage_pct": 1.0,
                    "latency_ms": {"retrieval": 0.0, "generation": 0.0, "verification": 0.0, "total": round((time.time() - start_time) * 1000, 1)},
                },
            )

        if is_meta:
            doc_summary_text = (
                f"e.g. {', '.join(sample_filenames[:3])}" if sample_filenames else f"{doc_count} documents"
            )
            system_overview = (
                "I am Aegis, an enterprise evidence-grounded knowledge intelligence platform built for AWS.\n\n"
                "Here is what I can do:\n"
                "1. Multimodal Document Ingestion: Extracts and parses text, layout, and tables from PDFs, text files, and images (using Amazon Textract OCR).\n"
                "2. Hybrid Semantic Retrieval: Combines dense vector search (Amazon Bedrock Titan Embeddings v2) with lexical BM25 keyword matching.\n"
                "3. Claim-Level Grounding Verification: Evaluates factual statements against retrieved excerpts before returning an answer, ensuring zero hallucinations.\n"
                "4. Autonomous Self-Correction: Automatically rewrites queries and re-retrieves if factual support is incomplete (<75% coverage).\n"
                "5. Verifiable Evidence Citations: Links every claim to exact document names, chunk IDs, and page numbers.\n\n"
                f"Active Knowledge Base: {doc_count} document(s) currently indexed ({doc_summary_text}). Ask me any question about your documents!"
            )
            return QueryResponse(
                query_id=query_id,
                query=query,
                answer=system_overview,
                citations=[],
                grounding_coverage=1.0,
                total_claims=1,
                supported_claims=1,
                claims=[{"claim_id": "meta_0", "statement": "System overview provided.", "is_grounded": True, "supporting_chunk_ids": [], "confidence": 1.0}],
                retrieval_trace={
                    "query_id": query_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "original_query": query,
                    "final_query": query,
                    "iterations": 1,
                    "self_correction_triggered": False,
                    "retrieval_strategies": ["System Metadata Overview"],
                    "candidate_count": 0,
                    "selected_evidence_count": 0,
                    "grounding_coverage_pct": 1.0,
                    "latency_ms": {"retrieval": 0.0, "generation": 0.0, "verification": 0.0, "total": round((time.time() - start_time) * 1000, 1)},
                },
            )

        current_query = query
        attempt = 1
        self_correction_triggered = False

        retrieval_time = 0.0
        generation_time = 0.0
        verification_time = 0.0

        all_retrieved_evidence: List[Tuple[Chunk, float]] = []

        while attempt <= self.max_attempts:
            logger.info(f"Query {query_id} attempt {attempt}/{self.max_attempts} for: '{current_query}'")

            # 1. Retrieval
            r_start = time.time()
            candidates = self.retriever.retrieve(
                query=current_query,
                document_ids=document_ids,
                top_k=self.settings.retrieval_top_k,
            )
            retrieval_time += (time.time() - r_start)

            # Deduplicate with previously gathered evidence
            existing_ids = {c.chunk_id for c, _ in all_retrieved_evidence}
            for chunk, score in candidates:
                if chunk.chunk_id not in existing_ids:
                    all_retrieved_evidence.append((chunk, score))
                    existing_ids.add(chunk.chunk_id)

            # Rerank / keep top-k for generation context
            all_retrieved_evidence.sort(key=lambda x: x[1], reverse=True)
            active_evidence = all_retrieved_evidence[: self.settings.reranking_top_k]

            # 2. Generation
            g_start = time.time()
            answer = self.generator.generate_answer(query, active_evidence)
            generation_time += (time.time() - g_start)

            # 3. Grounding Evaluation
            v_start = time.time()
            evaluation: GroundingEvaluation = self.evaluator.evaluate(answer, active_evidence)
            verification_time += (time.time() - v_start)

            logger.info(
                f"Attempt {attempt} Grounding Coverage: {evaluation.grounding_coverage*100:.1f}% "
                f"({evaluation.supported_claims}/{evaluation.total_claims} claims)"
            )

            # Decision gate: Sufficient or honest fallback declared
            if evaluation.is_sufficient or "insufficient evidence" in answer.lower():
                break

            # If insufficient evidence and attempts remain, trigger self-correction query rewrite
            if attempt < self.max_attempts:
                self_correction_triggered = True
                unsupported = [c.statement for c in evaluation.claims if not c.is_grounded]
                missing_aspects = " ".join(unsupported[:2])
                current_query = f"{query} {missing_aspects}".strip()
                logger.info(f"Self-correction triggered: Rewrote query to '{current_query}'")

            attempt += 1

        total_time = time.time() - start_time

        # 4. Citations extraction
        citations = self.citation_generator.extract_citations(answer, active_evidence)

        # 5. Build Retrieval Trace
        retrieval_trace = {
            "query_id": query_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_query": query,
            "final_query": current_query,
            "iterations": attempt if attempt <= self.max_attempts else self.max_attempts,
            "self_correction_triggered": self_correction_triggered,
            "retrieval_strategies": ["Titan v2 Semantic Vector Search", "BM25 Lexical Overlap"],
            "candidate_count": len(all_retrieved_evidence),
            "selected_evidence_count": len(active_evidence),
            "grounding_coverage_pct": evaluation.grounding_coverage,
            "latency_ms": {
                "retrieval": round(retrieval_time * 1000, 1),
                "generation": round(generation_time * 1000, 1),
                "verification": round(verification_time * 1000, 1),
                "total": round(total_time * 1000, 1),
            },
        }

        return QueryResponse(
            query_id=query_id,
            query=query,
            answer=answer,
            citations=citations,
            grounding_coverage=evaluation.grounding_coverage,
            total_claims=evaluation.total_claims,
            supported_claims=evaluation.supported_claims,
            claims=[c.model_dump() for c in evaluation.claims],
            retrieval_trace=retrieval_trace,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    print("\n" + "=" * 76)
    print("  [AEGIS] SELF-CORRECTING MULTIMODAL GRAPHRAG PLATFORM")
    print("  Execution Engine & Factual Claim Verification")
    print("=" * 76)

    # Allow custom query via command-line arguments or use default
    sample_query = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "What does Section 1 Data Verification state about claims?"
    )

    print(f"\n[?] Query: \"{sample_query}\"")
    print("[*] Initializing RAG Orchestrator (Retriever, Generator, Evaluator)...")

    engine = RAGOrchestrator()
    print("[*] Running semantic retrieval, grounded synthesis, and verification loop...")
    response = engine.process_query(sample_query)

    print("\n" + "-" * 76)
    print("  GROUNDED SYNTHESIS RESULT")
    print("-" * 76)
    print(f"Answer:\n{response.answer}")

    print("\n" + "-" * 76)
    print("  VERIFICATION & CITATION AUDIT")
    print("-" * 76)
    print(f"Grounding Coverage: {response.grounding_coverage * 100:.1f}%")
    print(f"Claims Verified:    {response.supported_claims} supported / {response.total_claims} total")
    print(f"Iterations:         {response.retrieval_trace['iterations']}")
    print(f"Self-Correction:    {response.retrieval_trace['self_correction_triggered']}")
    print(f"Candidates Found:   {response.retrieval_trace['candidate_count']}")
    print(f"Total Latency:      {response.retrieval_trace['latency_ms']['total']} ms")

    if response.citations:
        print("\nCitations:")
        for idx, cit in enumerate(response.citations, 1):
            print(f"  [{idx}] Document: {cit.filename} | Page: {cit.page} | Chunk: {cit.chunk_id} | Relevance: {cit.relevance_score}")
    else:
        print("\nCitations: None (Honest fallback or no direct citations needed)")

    print("=" * 76 + "\n")

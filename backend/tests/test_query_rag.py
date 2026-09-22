"""
Tests for Aegis Retrieval, Citation Generation, and Grounding Evaluation.
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.document import Chunk, ChunkMetadata
from backend.app.citations.generator import CitationGenerator
from backend.app.evaluation.grounding import ClaimGroundingEvaluator
from backend.app.retrieval.vector_search import cosine_similarity

client = TestClient(app)


def test_cosine_similarity():
    """Verify vector cosine similarity calculation."""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    vec3 = [0.0, 1.0, 0.0]

    assert abs(cosine_similarity(vec1, vec2) - 1.0) < 1e-4
    assert abs(cosine_similarity(vec1, vec3) - 0.0) < 1e-4


def test_citation_generator():
    """Verify citations are accurately extracted and mapped to evidence chunks."""
    generator = CitationGenerator()
    chunk = Chunk(
        chunk_id="doc1#p1_c0",
        document_id="doc1",
        text="Aegis features claim-level grounding verification to stop hallucinations.",
        metadata=ChunkMetadata(
            document_id="doc1",
            filename="architecture.pdf",
            page=1,
            section="Verification",
            chunk_index=0,
            source_type="pdf",
        ),
    )

    answer = "Aegis stops hallucinations using claim-level verification [Chunk: doc1#p1_c0]."
    citations = generator.extract_citations(answer, [(chunk, 0.95)])

    assert len(citations) == 1
    assert citations[0].document_id == "doc1"
    assert citations[0].filename == "architecture.pdf"
    assert citations[0].page == 1
    assert citations[0].chunk_id == "doc1#p1_c0"
    assert citations[0].relevance_score == 0.95


def test_claim_grounding_evaluator():
    """Verify claim decomposition and coverage calculation."""
    evaluator = ClaimGroundingEvaluator(threshold=0.75)
    chunk = Chunk(
        chunk_id="doc1#p2_c1",
        document_id="doc1",
        text="All cloud resources are encrypted with AES-256 by default. S3 buckets block public access.",
        metadata=ChunkMetadata(
            document_id="doc1",
            filename="security.txt",
            page=2,
            chunk_index=1,
            source_type="txt",
        ),
    )

    # 1. Test grounded answer
    grounded_answer = "All cloud resources are encrypted with AES-256 by default. S3 buckets block public access."
    eval1 = evaluator.evaluate(grounded_answer, [(chunk, 0.9)])
    assert eval1.total_claims >= 1
    assert eval1.grounding_coverage >= 0.75
    assert eval1.is_sufficient is True

    # 2. Test insufficient evidence honest statement
    honest_answer = "I couldn't find sufficient evidence in the uploaded sources to answer this confidently."
    eval2 = evaluator.evaluate(honest_answer, [])
    assert eval2.grounding_coverage == 1.0
    assert eval2.is_sufficient is True


def test_query_api_endpoint():
    """Verify /api/v1/query endpoint executes and returns structured response."""
    payload = {"query": "What is Aegis and how does it prevent hallucinations?"}
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "query_id" in data
    assert "answer" in data
    assert "citations" in data
    assert "grounding_coverage" in data
    assert "retrieval_trace" in data
    assert "latency_ms" in data["retrieval_trace"]

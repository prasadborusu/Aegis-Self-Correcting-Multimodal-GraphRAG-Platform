"""
Unit tests for Aegis Self-Correction Engine.
Verifies that difficult cross-document queries trigger multi-pass retrieval,
query reformulation, and consensus claim grounding.
"""
import pytest
from backend.app.rag.orchestrator import RAGOrchestrator


def test_cross_document_self_correction_triggering():
    """
    Test that a multi-aspect query asking to cross-reference multiple documents
    causes attempt 1 to detect missing evidence and triggers attempt 2.
    """
    orchestrator = RAGOrchestrator()
    query = "Cross-reference Durga Prasad academic percentage with his projects from his resume"

    response = orchestrator.process_query(query)

    assert response is not None
    assert response.retrieval_trace is not None
    assert response.retrieval_trace["self_correction_triggered"] is True
    assert response.retrieval_trace["iterations"] == 2
    assert response.grounding_coverage >= 0.75
    assert len(response.citations) >= 1

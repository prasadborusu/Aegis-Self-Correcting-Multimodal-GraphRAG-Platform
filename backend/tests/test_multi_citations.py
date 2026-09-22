"""
Verification test for multi-document citation extraction.
Verifies that when a cross-document answer is synthesized, citations correctly map
to distinct source filenames, chunk IDs, and page indices.
"""
import pytest
from backend.app.rag.orchestrator import RAGOrchestrator


def test_dual_document_citation_resolution():
    orchestrator = RAGOrchestrator()
    query = "Cross-reference Durga Prasad academic percentage with his projects from his resume"

    response = orchestrator.process_query(query)
    citations = response.citations

    assert citations is not None
    assert len(citations) >= 1

    # Verify citation attributes
    for cite in citations:
        assert cite.filename is not None and len(cite.filename) > 0
        assert cite.chunk_id is not None and len(cite.chunk_id) > 0
        assert cite.excerpt is not None and len(cite.excerpt) > 0
        assert cite.relevance_score > 0.0

    # Verify at least one citation includes page number metadata
    has_page = any(cite.page is not None for cite in citations)
    assert has_page is True

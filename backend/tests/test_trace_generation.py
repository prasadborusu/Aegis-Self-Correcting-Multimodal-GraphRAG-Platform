"""
Integration test for multi-pass retrieval trace generation and attempt history auditing.
Verifies that the orchestrator populates latency breakdowns, candidate counts,
and attempt-by-attempt grounding evaluations in the trace object.
"""
import pytest
from backend.app.rag.orchestrator import RAGOrchestrator


def test_retrieval_trace_structure_and_attempt_history():
    orchestrator = RAGOrchestrator()
    query = "Cross-reference Durga Prasad academic percentage with his projects from his resume"

    response = orchestrator.process_query(query)
    trace = response.retrieval_trace

    assert trace is not None
    assert "query_id" in trace
    assert "timestamp" in trace
    assert "original_query" in trace
    assert "final_query" in trace
    assert "iterations" in trace
    assert "self_correction_triggered" in trace
    assert "latency_ms" in trace
    assert "candidate_count" in trace
    assert "selected_evidence_count" in trace
    assert "grounding_coverage_pct" in trace

    # Validate latency breakdown sub-keys
    latencies = trace["latency_ms"]
    assert "retrieval" in latencies
    assert "generation" in latencies
    assert "verification" in latencies
    assert "total" in latencies

    # Validate attempt history for self-correction audit
    if trace["self_correction_triggered"]:
        attempt_history = trace.get("attempt_history", [])
        assert len(attempt_history) >= 2
        assert attempt_history[0]["attempt"] == 1
        assert attempt_history[1]["attempt"] == 2
        assert attempt_history[0]["is_sufficient"] is False
        assert attempt_history[1]["is_sufficient"] is True

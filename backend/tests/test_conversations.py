"""
Tests for Aegis Chat Persistence and Conversation Service.
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.conversation_service import ConversationService
from backend.app.rag.orchestrator import QueryResponse

client = TestClient(app)


def test_conversation_service_local_save_and_retrieve():
    """Verify messages are stored locally in .storage/conversations/ and retrieved accurately."""
    service = ConversationService()
    test_session = "test_unit_session"

    # Ensure clean slate
    service.clear_history(test_session)

    mock_response = QueryResponse(
        query_id="q_test_123",
        query="What is Aegis?",
        answer="Aegis is an evidence-first knowledge platform.",
        citations=[],
        grounding_coverage=1.0,
        total_claims=1,
        supported_claims=1,
        claims=[],
        retrieval_trace={
            "query_id": "q_test_123",
            "iterations": 1,
            "self_correction_triggered": False,
        },
    )

    service.save_turn(
        query="What is Aegis?",
        response=mock_response,
        session_id=test_session,
    )

    history = service.get_history(test_session)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "What is Aegis?"
    assert history[1].role == "assistant"
    assert "evidence-first" in history[1].content

    # Clean up
    service.clear_history(test_session)


def test_conversations_api_endpoints():
    """Verify GET and DELETE /api/v1/conversations endpoints."""
    # 1. Post a query to generate conversation
    client.post("/api/v1/query", json={"query": "hello", "session_id": "api_test_session"})

    # 2. Get history
    get_res = client.get("/api/v1/conversations?session_id=api_test_session")
    assert get_res.status_code == 200
    messages = get_res.json()
    assert len(messages) >= 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

    # 3. Clear history
    del_res = client.delete("/api/v1/conversations?session_id=api_test_session")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 4. Verify history is empty
    empty_res = client.get("/api/v1/conversations?session_id=api_test_session")
    assert empty_res.status_code == 200
    assert len(empty_res.json()) == 0

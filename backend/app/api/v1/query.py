"""
Query and RAG Execution API Endpoint for Aegis.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.rag.orchestrator import RAGOrchestrator, QueryResponse
from backend.app.services.conversation_service import ConversationService

router = APIRouter(prefix="/query", tags=["Query Engine"])
orchestrator = RAGOrchestrator()
conversation_service = ConversationService()


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Question to answer against uploaded sources")
    document_ids: Optional[List[str]] = Field(None, description="Optional scoped document IDs")
    session_id: Optional[str] = Field("default", description="Conversation session identifier")


@router.post("", response_model=QueryResponse, status_code=status.HTTP_200_OK)
def execute_query(request: QueryRequest) -> QueryResponse:
    """
    Execute an evidence-grounded query with claim verification, citation generation, and self-correction.
    Automatically saves the chat turn locally to .storage/conversations/ and syncs with DynamoDB.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        response = orchestrator.process_query(
            query=request.query,
            document_ids=request.document_ids,
        )
        # Automatically persist chat turn locally and to DynamoDB
        conversation_service.save_turn(
            query=request.query,
            response=response,
            session_id=request.session_id or "default",
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

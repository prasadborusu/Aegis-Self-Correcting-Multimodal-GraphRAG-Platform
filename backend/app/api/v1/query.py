"""
Query and RAG Execution API Endpoint for Aegis.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.rag.orchestrator import RAGOrchestrator, QueryResponse

router = APIRouter(prefix="/query", tags=["Query Engine"])
orchestrator = RAGOrchestrator()


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Question to answer against uploaded sources")
    document_ids: Optional[List[str]] = Field(None, description="Optional scoped document IDs")


@router.post("", response_model=QueryResponse, status_code=status.HTTP_200_OK)
def execute_query(request: QueryRequest) -> QueryResponse:
    """
    Execute an evidence-grounded query with claim verification, citation generation, and self-correction.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        response = orchestrator.process_query(
            query=request.query,
            document_ids=request.document_ids,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

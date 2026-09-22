"""
Conversations and Chat History API Endpoints for Aegis.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, status
from pydantic import BaseModel

from backend.app.services.conversation_service import ConversationService, ChatMessage

router = APIRouter(prefix="/conversations", tags=["Conversations"])
conversation_service = ConversationService()


class ClearResponse(BaseModel):
    success: bool
    message: str


@router.get("", response_model=List[ChatMessage], status_code=status.HTTP_200_OK)
def get_conversation_history(session_id: str = Query("default", description="Session identifier")) -> List[ChatMessage]:
    """
    Retrieve stored chat history for a session from local .storage/conversations/ folder.
    """
    return conversation_service.get_history(session_id=session_id)


@router.delete("", response_model=ClearResponse, status_code=status.HTTP_200_OK)
def clear_conversation_history(session_id: str = Query("default", description="Session identifier")) -> ClearResponse:
    """
    Clear stored chat history for a session from local storage.
    """
    success = conversation_service.clear_history(session_id=session_id)
    return ClearResponse(
        success=success,
        message="Conversation history cleared successfully." if success else "Failed to clear history.",
    )

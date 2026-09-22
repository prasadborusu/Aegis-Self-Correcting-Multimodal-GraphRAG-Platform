"""
Conversation History and Chat Persistence Service for Aegis.
Saves chat history locally to .storage/conversations/ with automatic DynamoDB synchronization.
"""

import json
import uuid
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import ClientError

from backend.app.config.settings import Settings, get_settings
from backend.app.models.document import Citation
from backend.app.rag.orchestrator import QueryResponse

logger = logging.getLogger("aegis.conversations")


class ChatMessage(BaseModel):
    message_id: str
    role: str  # "user" | "assistant"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    citations: List[Citation] = Field(default_factory=list)
    grounding_coverage: Optional[float] = None
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    trace: Optional[Dict[str, Any]] = None


class ConversationService:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.table_name = self.settings.dynamodb_conversations_table
        self.region = self.settings.aws_region

        # Local storage directory for chat persistence
        self.storage_dir = Path("./.storage/conversations")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._dynamodb_resource = None

    @property
    def dynamodb(self):
        if self._dynamodb_resource is None:
            self._dynamodb_resource = boto3.resource("dynamodb", region_name=self.region)
        return self._dynamodb_resource

    def _get_session_file(self, session_id: str = "default") -> Path:
        # Sanitize session_id for filesystem
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("-", "_")).strip() or "default"
        return self.storage_dir / f"{safe_id}.json"

    def get_history(self, session_id: str = "default") -> List[ChatMessage]:
        """
        Load conversation history from local .storage/conversations/ folder.
        """
        file_path = self._get_session_file(session_id)
        if not file_path.exists():
            return []

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            return [ChatMessage(**item) for item in data]
        except Exception as e:
            logger.error(f"Failed to read local chat history from {file_path}: {e}")
            return []

    def save_turn(
        self,
        query: str,
        response: QueryResponse,
        session_id: str = "default",
    ) -> List[ChatMessage]:
        """
        Append user query and assistant response to local JSON file and sync to DynamoDB.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        user_msg = ChatMessage(
            message_id=str(uuid.uuid4()),
            role="user",
            content=query,
            timestamp=now_str,
        )

        assistant_msg = ChatMessage(
            message_id=response.query_id or str(uuid.uuid4()),
            role="assistant",
            content=response.answer,
            timestamp=datetime.now(timezone.utc).isoformat(),
            citations=response.citations,
            grounding_coverage=response.grounding_coverage,
            claims=response.claims,
            trace=response.retrieval_trace,
        )

        # 1. Update local storage JSON file
        history = self.get_history(session_id)
        history.extend([user_msg, assistant_msg])

        file_path = self._get_session_file(session_id)
        try:
            dumped = [m.model_dump() for m in history]
            file_path.write_text(json.dumps(dumped, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"Saved {len(history)} messages to local file {file_path}")
        except Exception as e:
            logger.error(f"Failed to write chat history to {file_path}: {e}")

        # 2. Sync to DynamoDB if available
        try:
            table = self.dynamodb.Table(self.table_name)
            table.put_item(
                Item={
                    "conversation_id": session_id,
                    "query_id": response.query_id,
                    "query": query,
                    "answer": response.answer,
                    "grounding_coverage": str(response.grounding_coverage),
                    "timestamp": now_str,
                }
            )
        except ClientError as e:
            logger.debug(f"DynamoDB conversation sync skipped: {e}")
        except Exception as e:
            logger.debug(f"DynamoDB sync failed: {e}")

        return [user_msg, assistant_msg]

    def clear_history(self, session_id: str = "default") -> bool:
        """
        Clear conversation history for a session.
        """
        file_path = self._get_session_file(session_id)
        if file_path.exists():
            try:
                file_path.write_text("[]", encoding="utf-8")
                return True
            except Exception as e:
                logger.error(f"Failed to clear chat history in {file_path}: {e}")
                return False
        return True

from enum import Enum
from pydantic import BaseModel, Field

class ProcessingState(str, Enum):
    UPLOADED = 'UPLOADED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

class ChunkMetadata(BaseModel):
    document_id: str
    filename: str
    page: int = 1
    chunk_index: int = 0

class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    metadata: ChunkMetadata

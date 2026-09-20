from enum import Enum
from pydantic import BaseModel, Field

class ProcessingState(str, Enum):
    UPLOADED = 'UPLOADED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

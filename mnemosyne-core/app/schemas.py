from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class MemoryMetadata(BaseModel):
    location: Optional[str] = None
    category: Optional[str] = None
    sentiment: Optional[float] = None
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())

class MemoryEntry(BaseModel):
    content: str
    metadata: MemoryMetadata = Field(default_factory=MemoryMetadata)

class MemoryResponse(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None
    base64_content: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    n_results: int = 3

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

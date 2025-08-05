from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    topic: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    topic: Optional[str] = None
    sources: List[str] = []
    session_id: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatSession(BaseModel):
    id: str
    user_id: str
    topic: Optional[str] = None
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
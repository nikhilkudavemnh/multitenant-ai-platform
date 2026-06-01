from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateConversationRequest(BaseModel):
    title: str


class ChatRequest(BaseModel):
    message: str


class ConversationResponse(BaseModel):
    thread_id: UUID
    user_id: int
    title: str
    created_date: datetime


class ChatResponse(BaseModel):
    thread_id: UUID
    response: str

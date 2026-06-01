from uuid import UUID

from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_tenant_db
from src.schemas.agent_schemas import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    CreateConversationRequest,
)
from src.service.agent_service import AgentService
from src.util.auth import get_current_user

agent_router = APIRouter(prefix="/agent", tags=["Agent"])


@agent_router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
        request: CreateConversationRequest,
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_tenant_db),
):
    return await AgentService(db).create_conversation(current_user["user_id"], request)


@agent_router.get("/conversations/{limit}/{offset}", response_model=list[ConversationResponse])
async def list_conversations(
        limit: int = 1000,
        offset: int = 0,
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_tenant_db),
):
    return await AgentService(db).list_conversations(current_user["user_id"], limit, offset)


@agent_router.post("/conversations/{thread_id}/chat", response_model=ChatResponse)
async def chat(
        thread_id: UUID,
        request: ChatRequest,
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_tenant_db),
        short_name: str = Header(...,alias="X-Tenant")
):
    return await AgentService(db).chat(thread_id, current_user["user_id"], short_name, request)


@agent_router.post("/conversations/{thread_id}/chat/stream")
async def chat_stream(
        thread_id: UUID,
        request: ChatRequest,
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_tenant_db),
        short_name: str = Header(...,alias="X-Tenant")
):
    return StreamingResponse(
        AgentService(db).stream_chat(thread_id, short_name, current_user["user_id"], request),
        media_type="text/event-stream",
    )

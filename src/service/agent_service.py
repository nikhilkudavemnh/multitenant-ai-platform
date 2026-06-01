import json
from typing import AsyncGenerator
from uuid import UUID

from fastapi import HTTPException, status, Request
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.graph import get_agent
from src.repository.conversation_repository import ConversationRepository
from src.repository.tenant_repository import TenantRepository
from src.schemas.agent_schemas import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    CreateConversationRequest,
)
from src.service.tenant_service import TenantService


class AgentService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._repo = ConversationRepository(db)
        self._tenant = TenantRepository(db)

    async def create_conversation(self, user_id: int, request: CreateConversationRequest) -> ConversationResponse:
        conv = await self._repo.create(user_id, request.title)
        return ConversationResponse(
            thread_id=conv.thread_id,
            user_id=conv.user_id,
            title=conv.title,
            created_date=conv.created_date,
        )

    async def list_conversations(self, user_id: int, limit:int, offset:int) -> list[ConversationResponse]:
        convs = await self._repo.list_by_user(user_id, limit, offset)
        return [
            ConversationResponse(
                thread_id=c.thread_id,
                user_id=c.user_id,
                title=c.title,
                created_date=c.created_date,
            )
            for c in convs
        ]

    async def _get_verified_conversation(self, thread_id: UUID, user_id: int):
        conv = await self._repo.get_by_id(thread_id)
        if conv is None or conv.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {thread_id} not found",
            )
        return conv

    async def chat(self, thread_id: UUID, user_id: int, short_name:str, chat_request: ChatRequest, ) -> ChatResponse:
        await self._get_verified_conversation(thread_id, user_id)
        tenant_obj = await self._tenant.get_by_short_name(short_name)
        agent = await get_agent(tenant_obj.__getattribute__("schema"))
        config = {"configurable": {"thread_id": str(thread_id)}}
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=chat_request.message)]},
            config=config,
        )
        last = result["messages"][-1]
        content = last.content
        if isinstance(content, list):
            response_text = "".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            response_text = content
        return ChatResponse(thread_id=thread_id, response=response_text)

    async def stream_chat(
        self,
            thread_id: UUID,
            user_id: int,
            short_name: str,
            request: ChatRequest
    ) -> AsyncGenerator[str, None]:
        await self._get_verified_conversation(thread_id, user_id)
        tenant_obj = await self._tenant.get_by_short_name(short_name)
        agent = await get_agent(tenant_obj.__getattribute__("schema"))
        config = {"configurable": {"thread_id": str(thread_id)}}
        async for event in agent.astream_events(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
            version="v2",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                content = chunk.content
                if isinstance(content, str) and content:
                    yield f"data: {json.dumps({'token': content})}\n\n"
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text" and block.get("text"):
                            yield f"data: {json.dumps({'token': block['text']})}\n\n"
            elif kind == "on_tool_start":
                yield f"data: {json.dumps({'event': 'tool_start', 'tool': event.get('name', '')})}\n\n"
            elif kind == "on_tool_end":
                yield f"data: {json.dumps({'event': 'tool_end', 'tool': event.get('name', '')})}\n\n"
        yield "data: [DONE]\n\n"

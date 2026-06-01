from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.langgraph_model import Conversation


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, user_id: int, title: str) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self._db.add(conv)
        await self._db.flush()
        await self._db.refresh(conv)
        return conv

    async def get_by_id(self, thread_id: UUID) -> Conversation | None:
        result = await self._db.execute(
            select(Conversation).where(Conversation.thread_id == thread_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int, limit:int, offset:int) -> list[Conversation]:
        result = await self._db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_date.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

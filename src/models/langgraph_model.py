from sqlalchemy import String, BIGINT, func, DateTime, Index
from src.database.db import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import UUID
from uuid_utils import uuid7
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversation"
    __table_args__ = (Index("idx_conversation_thread_id", "thread_id"),
                      Index("idx_conversation_user_id", "user_id"),)

    thread_id : Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_id : Mapped[int] = mapped_column(BIGINT, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


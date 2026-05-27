from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, BIGINT, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from src.database.db import Base
from sqlalchemy.dialects.postgresql import JSONB


class Client(Base):
    __tablename__ = "client"
    __table_args__ = {"schema": "public"}

    id:Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    schema:Mapped[str] = mapped_column(String, nullable=False)
    name:Mapped[str] = mapped_column(String(250), nullable=False)
    short_name:Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), nullable=False)
    created_date:Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    expiry_date:Mapped[DateTime] = mapped_column(DateTime)
    api_key_hash:Mapped[String] = mapped_column(String)
    setting:Mapped[JSONB] = mapped_column(JSONB, default={})





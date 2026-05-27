from datetime import datetime
from sqlalchemy import BIGINT, Boolean, DateTime, ForeignKey, Index, String, func, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("idx_users_email", "email"),
                      Index("idx_users_user_id", "user_id"),
                      )

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    auth_provider: Mapped[str] = mapped_column(String(50), default="local", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                   onupdate=func.now(), nullable=False)
    last_login_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int] = mapped_column(BIGINT, nullable=False)
    updated_by: Mapped[int] = mapped_column(BIGINT, nullable=False)
    user_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    refresh_token_hash: Mapped[str | None] = mapped_column(String(255))
    refresh_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    role: Mapped["Role"] = relationship("Role", lazy="joined")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (Index("idx_role_id", "role_id"),)

    role_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    permissions: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by: Mapped[int] = mapped_column(BIGINT, nullable=False)

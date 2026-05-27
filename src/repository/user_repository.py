import hashlib
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth_model import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Insert a new user; sets updated_by to the generated user_id after flush."""
        self._db.add(user)
        await self._db.flush()
        user.updated_by = user.user_id
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def save(self, user: User) -> User:
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def list_all(self) -> list[User]:
        result = await self._db.execute(select(User).order_by(User.user_id))
        return list(result.scalars().all())

    async def get_by_refresh_token(self, raw_token: str) -> User | None:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        result = await self._db.execute(
            select(User).where(
                User.refresh_token_hash == token_hash,
                User.refresh_token_expires_at > datetime.now(UTC),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> User | None:
        result = await self._db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

from typing import AsyncGenerator

from fastapi import Header, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import quoted_name

_session_factory: async_sessionmaker[AsyncSession] | None = None

class Base(DeclarativeBase):
    pass

def init_db(engine: AsyncEngine) -> None:
    #Creates reusable Global session factory using engine.
    global _session_factory
    _session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autoflush=False,
    )
    """ expire_on_commit = False
        - objects remain accessible after commit
        - avoids unnecessary reload queries
    """


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        raise RuntimeError("Database not initialized")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_tenant_db(
    x_tenant: str = Header(..., alias="X-Tenant"),
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AsyncSession, None]:
    result = await db.execute(
        text("SELECT schema FROM public.client WHERE short_name = :short_name"),
        {"short_name": x_tenant},
    )
    schema = result.scalar_one_or_none()

    if schema is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenant '{x_tenant}' not found")
    safe_schema = quoted_name(schema, quote=True)
    await db.execute(text(f'SET search_path TO {safe_schema}'))
    yield db
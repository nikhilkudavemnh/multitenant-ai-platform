import uvicorn

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.core.setting import settings
from src.database.db import init_db, get_db
import src.models  # noqa: F401 — registers all models with Base.metadata
from src.service.tenant_service import PublicSchemaInitializer
from src.util.request_response_middleware import RequestResponseMiddleware
from src.util.auth import get_current_user
from src.api.auth import auth_router
from src.api.tenant import tenant_router
from src.repository.tenant_repository import TenantRepository


DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    pool_use_lifo=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(engine)

    public_schema = PublicSchemaInitializer(engine)
    await public_schema.initialize_public_schema()

    yield

    await engine.dispose()


app = FastAPI(
    title="multitenant-ai-platform",
    version="1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestResponseMiddleware)



# add future routers here with: dependencies=[Depends(get_current_user)]

@app.get("/health", tags=["health"])
async def health():
    return {
        "message": "success",
        "status": 200,
    }


@app.get("/healthcheck-full", tags=["health"])
async def healthcheck(
    db: AsyncSession = Depends(get_db),
):
    await db.execute(text("SELECT 1"))

    return {
        "message": "success",
        "status": 200,
    }


app.include_router(tenant_router, dependencies=[Depends(TenantRepository.verify_admin_user)])
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
    )
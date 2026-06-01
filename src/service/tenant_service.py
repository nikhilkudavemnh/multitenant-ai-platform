import hashlib
import secrets
from sqlalchemy.ext.asyncio import AsyncEngine
from src.database.db import Base
from src.repository.tenant_repository import TenantRepository
from src.util.exceptions import TenantAlreadyExistsError, TenantNotFoundError
from src.models.tenant_model import Client
from src.schemas.tenant_schemas import (
    CreateTenantRequest, CreateTenantResponse,
    DeleteTenantRequest,
    ListTenantRequest,
    UpdateTenantRequest, UpdateTenantResponse,
)


class PublicSchemaInitializer:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def initialize_public_schema(self) -> None:
        public_tables = [
            table for table in Base.metadata.tables.values()
            if table.schema == "public"
        ]
        async with self._engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    bind=sync_conn, tables=public_tables,
                )
            )


class TenantService:
    def __init__(self, repo: TenantRepository):
        self._repo = repo

    async def create_tenant(self, request: CreateTenantRequest) -> CreateTenantResponse:
        existing = await self._repo.get_by_short_name(request.short_name)

        if existing:
            raise TenantAlreadyExistsError(request.short_name)

        api_key = secrets.token_urlsafe(32)
        schema_name = f"tenant_{request.short_name}"

        client = Client(
            name=request.name,
            short_name=request.short_name,
            plan=request.plan,
            expiry_date=request.expiry_date,
            schema=schema_name,
            api_key_hash=hashlib.sha256(api_key.encode()).hexdigest(),
        )

        client = await self._repo.save(client)
        await self._repo.create_schema(client.schema)

        return CreateTenantResponse(
            name=client.name,
            shortName=client.short_name,
            plan=client.plan,
            expiryDate=str(client.expiry_date),
        )

    async def update(self, request: UpdateTenantRequest) -> UpdateTenantResponse:
        client = await self._repo.get_by_id(request.id)
        if not client:
            raise TenantNotFoundError(str(request.id))

        client.name = request.name
        client.short_name = request.short_name
        client.plan = request.plan
        client.expiry_date = request.expiry_date

        client = await self._repo.save(client)
        return UpdateTenantResponse(
            id=client.id,
            name=client.name,
            short_name=client.short_name,
            plan=client.plan,
        )

    async def delete(self, request: DeleteTenantRequest) -> dict:
        client = await self._repo.get_by_id(request.id)
        if not client:
            raise TenantNotFoundError(str(request.id))
        if client.short_name != request.short_name:
            raise TenantNotFoundError(f"{request.id}/{request.short_name}")
        await self._repo.delete(client)
        return {"deleted": request.id}

    async def get_list(self, request: ListTenantRequest) -> list[dict]:
        clients = await self._repo.get_list(
            order=request.orderBy,
            active_only=request.enable,
        )
        return [
            {
                "id": c.id,
                "name": c.name,
                "shortName": c.short_name,
                "schema": c.schema,
                "plan": c.plan,
                "expiryDate": str(c.expiry_date),
            }
            for c in clients
        ]

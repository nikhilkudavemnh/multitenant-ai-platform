from datetime import datetime, UTC
from fastapi import Request, Header
from sqlalchemy import select, desc, asc, text, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tenant_model import Client
from src.database.db import Base
from src.core.setting import settings
from src.util.auth import verify_password

class TenantRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, tenant_id: int) -> Client | None:
        result = await self._db.execute(select(Client).where(Client.id == tenant_id))
        return result.scalars().first()

    async def get_by_short_name(self, short_name: str) -> Client | None:
        result = await self._db.execute(select(Client).where(Client.short_name == short_name))
        return result.scalars().first()

    async def save(self, client: Client) -> Client:
        self._db.add(client)
        await self._db.flush()
        await self._db.refresh(client)
        return client

    async def delete(self, client: Client) -> None:
        await self._db.delete(client)
        await self._db.commit()

    async def get_list(self, order: str = "desc", active_only: bool = False) -> list[Client]:
        query = select(Client)
        if active_only:
            now_utc = datetime.now(UTC).replace(tzinfo=None)
            query = query.where(
                or_(Client.expiry_date == None, Client.expiry_date > now_utc)
            )
        order_fn = desc if order == "desc" else asc
        query = query.order_by(order_fn(Client.id))
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def create_schema(self, schema_name: str):
        await self._db.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
        )
        private_tables = [
            table for table in Base.metadata.tables.values()
            if table.schema != "public"
        ]
        conn = await self._db.connection()
        await conn.execute(text(f'SET search_path TO "{schema_name}"'))
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                bind=sync_conn, tables=private_tables,
            )
        )
        # Roles inserted first; created_by=1 because system user will get user_id=1 (first sequence value)
        await conn.execute(text(
            f'INSERT INTO "{schema_name}".roles (role_name, permissions, is_active, created_by) '
            f"VALUES ('admin', '{{}}', true, 1), ('employee', '{{}}', true, 1)"
        ))
        await conn.execute(
            text(
                f'INSERT INTO "{schema_name}".users '
                f'(first_name, last_name, email, role_id, password_hash, auth_provider, is_active, created_by, updated_by, user_metadata) '
                f"VALUES ("
                f"  'System', 'User', :email, "
                f"  (SELECT role_id FROM \"{schema_name}\".roles WHERE role_name = 'admin'), "
                f"  :password_hash, 'local', true,1,  1, '{{}}'"
                f")"
            ),
            {"email": settings.ADMIN_EMAIL, "password_hash": settings.ADMIN_PASSWORD_HASH},
        )

    @staticmethod
    async def verify_admin_user(admin_password:str = Header(..., alias="X-Admin-Password", description="The password of the admin user")):
        return verify_password(admin_password, settings.ADMIN_PASSWORD_HASH)


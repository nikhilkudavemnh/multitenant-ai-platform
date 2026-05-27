from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.util.exceptions import TenantAlreadyExistsError, TenantNotFoundError
from src.repository.tenant_repository import TenantRepository
from src.schemas.tenant_schemas import (
    CreateTenantRequest, UpdateTenantRequest, DeleteTenantRequest, ListTenantRequest,
)
from src.service.tenant_service import TenantService

tenant_router = APIRouter(
    prefix="/tenant",
    tags=["Tenant"],
)


def get_tenant_service(db: AsyncSession = Depends(get_db)) -> TenantService:
    return TenantService(TenantRepository(db))


@tenant_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: CreateTenantRequest,
    service: TenantService = Depends(get_tenant_service),
):
    try:
        return await service.create_tenant(request)
    except TenantAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@tenant_router.post("/update")
async def update_tenant(
    request: UpdateTenantRequest,
    service: TenantService = Depends(get_tenant_service),
):
    try:
        return await service.update(request)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@tenant_router.delete("/delete")
async def delete_tenant(
    request: DeleteTenantRequest,
    service: TenantService = Depends(get_tenant_service),
):
    try:
        return await service.delete(request)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@tenant_router.post("/list")
async def list_tenant(
    request: ListTenantRequest,
    service: TenantService = Depends(get_tenant_service),
):
    return await service.get_list(request)

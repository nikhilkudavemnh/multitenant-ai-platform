from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_tenant_db
from src.schemas.auth_shemas import (
    LoginRequest, LoginResponse,
    LogoutRequest, LogoutResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    SignupRequest, SignupResponse,
)
from src.service.auth_service import AuthenticationService
from src.util.auth import get_current_user

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/signup", response_model=SignupResponse)
async def signup(
    request: SignupRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    return await AuthenticationService(db).signup(current_user["user_id"], request)


@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_tenant_db)):
    return await AuthenticationService(db).login(request)


@auth_router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh(request: RefreshTokenRequest, db: AsyncSession = Depends(get_tenant_db)):
    return await AuthenticationService(db).refresh(request)


@auth_router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: dict = Depends(get_current_user),
                 db: AsyncSession = Depends(get_tenant_db)):
    return await AuthenticationService(db).logout(current_user["user_id"])

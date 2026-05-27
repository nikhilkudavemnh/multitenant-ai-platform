import hashlib
from datetime import datetime, UTC

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.setting import settings
from src.models.auth_model import User
from src.repository.user_repository import UserRepository
from src.schemas.auth_shemas import (
    LoginRequest, LoginResponse,
    LogoutRequest, LogoutResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    SignupRequest, SignupResponse,
)
from src.util.auth import get_password_hash, verify_password, create_access_token, create_refresh_token


class AuthenticationService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db=db)

    async def signup(self, user_id:int ,request: SignupRequest) -> SignupResponse:
        existing = await self.repo.get_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        new_user = User(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            password_hash=get_password_hash(request.password),
            role_id=2,
            updated_by= user_id,
            created_by= user_id
        )
        new_user = await self.repo.create(new_user)
        return SignupResponse(email=new_user.email, userId=new_user.user_id)

    async def login(self, request: LoginRequest) -> LoginResponse:
        user = await self.repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        access_token = create_access_token({
            "user_id": user.user_id,
            "email": user.email,
            "role_id": user.role_id,
        })
        raw_refresh, token_hash = create_refresh_token()

        user.refresh_token_hash = token_hash
        user.refresh_token_expires_at = datetime.now(UTC) + settings.JWT_REFRESH_EXPIRATION_DELTA
        user.last_login_date = datetime.now(UTC)
        await self.repo.save(user)

        return LoginResponse(
            accessToken=access_token,
            tokenType="bearer",
            refreshToken=raw_refresh,
        )

    async def refresh(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
        user = await self.repo.get_by_refresh_token(request.refresh_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        access_token = create_access_token({
            "user_id": user.user_id,
            "email": user.email,
            "role_id": user.role_id,
        })
        return RefreshTokenResponse(accessToken=access_token, tokenType="bearer")

    async def logout(self, user_id:int) -> LogoutResponse:
        user = await self.repo.get_by_user_id(user_id)
        if user:
            user.refresh_token_hash = None
            user.refresh_token_expires_at = None
            await self.repo.save(user)
        return LogoutResponse(message="Logged out successfully")

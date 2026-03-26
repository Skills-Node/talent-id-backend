from typing import Optional
from datetime import timedelta, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import UserRepository, RefreshTokenRepository
from schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
)
from core import (
    verify_password,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_refresh_token,
    NotFoundException,
    UnauthorizedException,
)
from config import get_settings
import uuid

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register(self, user_data: UserCreate) -> TokenResponse:
        await self.user_repo.create(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        return await self.login(login_data)

    async def login(self, credentials: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})

        token_id = str(uuid.uuid4())
        token_hash = get_password_hash(token_id)

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        await self.token_repo.create(
            user_id=user.id,
            token_id=token_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=f"{token_id}.{refresh_token}",
        )

    async def refresh_tokens(
        self, refresh_request: RefreshTokenRequest
    ) -> TokenResponse:
        parts = refresh_request.refresh_token.split(".")
        if len(parts) != 3:
            raise UnauthorizedException("Invalid refresh token format")

        token_id = parts[0]
        jwt_token = ".".join(parts[1:])

        try:
            payload = verify_refresh_token(jwt_token)
        except Exception:
            raise UnauthorizedException("Invalid refresh token")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Invalid refresh token")

        token_hash = get_password_hash(token_id)
        stored_token = await self.token_repo.get_by_hash(token_hash)
        if not stored_token or stored_token.token_id != token_id:
            raise UnauthorizedException("Invalid refresh token")

        await self.token_repo.revoke(stored_token.token_id)

        access_token = create_access_token(data={"sub": user.id})
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        new_token_id = str(uuid.uuid4())

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        await self.token_repo.create(
            user_id=user.id,
            token_id=new_token_id,
            token_hash=get_password_hash(new_token_id),
            expires_at=expires_at,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=f"{new_token_id}.{new_refresh_token}",
        )

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = user_data.password
        user = await self.user_repo.update(user_id, **update_data)
        return UserResponse.model_validate(user)

    async def logout(self, user_id: str) -> None:
        await self.token_repo.revoke_all_for_user(user_id)

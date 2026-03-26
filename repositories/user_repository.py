from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, RefreshToken
from core import get_password_hash, NotFoundException, ConflictException
import uuid


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, password: str, full_name: str) -> User:
        existing = await self.get_by_email(email)
        if existing:
            raise ConflictException("User with this email already exists")

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: str, **kwargs) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                if key == "password":
                    setattr(user, "hashed_password", get_password_hash(value))
                else:
                    setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: str) -> None:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        await self.db.delete(user)
        await self.db.commit()


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: str, token_id: str, token_hash: str, expires_at
    ) -> RefreshToken:
        token = RefreshToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_id=token_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                not RefreshToken.revoked,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_token_id(self, token_id: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_id == token_id,
                not RefreshToken.revoked,
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, token_id: str) -> None:
        token = await self.get_by_token_id(token_id)
        if token:
            token.revoked = True
            await self.db.commit()

    async def revoke_all_for_user(self, user_id: str) -> None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                not RefreshToken.revoked,
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked = True
        await self.db.commit()

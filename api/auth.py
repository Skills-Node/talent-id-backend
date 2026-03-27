from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import get_db, get_current_user_id
from services import AuthService
from schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.register(user_data)
    login_data = UserLogin(
        email=user_data.email, password=user_data.password
    )  # pragma: no cover
    return await service.login(login_data)  # pragma: no cover


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.login(credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)  # pragma: no cover
    return await service.refresh_tokens(refresh_request)  # pragma: no cover


@router.post("/logout")
async def logout(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.logout(user_id)
    return {"message": "Successfully logged out"}  # pragma: no cover


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.get_user_by_id(user_id)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.update_user(user_id, user_data)

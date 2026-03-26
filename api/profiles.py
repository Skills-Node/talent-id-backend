from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import get_db, get_current_user_id
from services import ProfileService
from schemas import (
    PerfilRequestInput,
    PerfilResponseOutput,
    ProfileResponse,
    ProfileListResponse,
    ProfileCreateResponse,
)

router = APIRouter(prefix="/profiles", tags=["Profiles"])


def get_profile_service(db: AsyncSession = Depends(get_db), gemini_client=None):
    return ProfileService(db, gemini_client)


@router.post("", response_model=ProfileCreateResponse, status_code=201)
async def create_profile(
    request: PerfilRequestInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    gemini_client=None,
):
    service = ProfileService(db, gemini_client)
    return await service.create_profile(user_id, request)


@router.get("", response_model=ProfileListResponse)
async def list_profiles(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    gemini_client=None,
):
    service = ProfileService(db, gemini_client)
    return await service.list_profiles(user_id)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    gemini_client=None,
):
    service = ProfileService(db, gemini_client)
    return await service.get_profile(user_id, profile_id)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    gemini_client=None,
):
    service = ProfileService(db, gemini_client)
    await service.delete_profile(user_id, profile_id)

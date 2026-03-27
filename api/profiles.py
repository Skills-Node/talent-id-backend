from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from core import get_db, get_current_user_id
from services import ProfileService
from schemas import (
    ProfileRequestInput,
    ProfileAIOutput,
    ProfileResponse,
    ProfileListResponse,
    ProfileCreateResponse,
)

router = APIRouter(prefix="/profiles", tags=["Profiles"])


def get_profile_service(
    db: AsyncSession = Depends(get_db), request: Request = None
):  # pragma: no cover
    ollama_client = request.app.state.ollama_client if request else None
    return ProfileService(db, ollama_client)


@router.post("", response_model=ProfileCreateResponse, status_code=201)
async def create_profile(
    request: ProfileRequestInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    req: Request = None,
):
    ollama_client = req.app.state.ollama_client if req else None
    service = ProfileService(db, ollama_client)
    return await service.create_profile(user_id, request)


@router.get("", response_model=ProfileListResponse)
async def list_profiles(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ProfileService(db, None)
    return await service.list_profiles(user_id)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ProfileService(db, None)
    return await service.get_profile(user_id, profile_id)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ProfileService(db, None)
    await service.delete_profile(user_id, profile_id)

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import get_db, get_current_user_id
from services import MatchingService
from schemas import (
    MatchingRequestInput,
    MatchingAIOutput,
    MatchingResponse,
    MatchingListResponse,
    MatchingCreateResponse,
)

router = APIRouter(prefix="/matchings", tags=["Matching"])


@router.post("", response_model=MatchingCreateResponse, status_code=201)
async def create_matching(
    request: MatchingRequestInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    gemini_client=None,
):
    service = MatchingService(db, gemini_client)
    return await service.create_matching(user_id, request)


@router.get("/profile/{profile_id}", response_model=MatchingListResponse)
async def list_matchings_by_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_db),
    gemini_client=None,
):
    service = MatchingService(db, gemini_client)
    return await service.list_matchings(profile_id)


@router.get("/{matching_id}", response_model=MatchingResponse)
async def get_matching(
    matching_id: str,
    db: AsyncSession = Depends(get_db),
    gemini_client=None,
):
    service = MatchingService(db, gemini_client)
    return await service.get_matching(matching_id)


@router.delete("/{matching_id}", status_code=204)
async def delete_matching(
    matching_id: str,
    db: AsyncSession = Depends(get_db),
    gemini_client=None,
):
    service = MatchingService(db, gemini_client)
    await service.delete_matching(matching_id)

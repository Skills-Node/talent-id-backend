from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from schemas.talent_service import (
    CompanyCreate,
    JobCreate,
    JobResponse,
    JobListResponse,
    CandidateSearchRequest,
    CandidateListResponse,
    OfferCreate,
    OfferResponse,
    OfferActionResponse,
    OfferListResponse,
)
from services.talent_service import talent_service
from core import get_current_user_id

router = APIRouter(prefix="/talent", tags=["talent"])


@router.post("/register-company", status_code=201)
async def register_company(
    company_data: CompanyCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Register a company on the blockchain"""
    result = await talent_service.register_company(
        wallet_address=user_id, company_data=company_data
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400, detail=result.get("error", "Failed to register company")
        )

    return result


@router.get("/jobs", response_model=JobListResponse)
async def get_active_jobs(
    limit: int = 20,
    offset: int = 0,
):
    """Get all active job postings"""
    jobs = await talent_service.get_active_jobs(limit, offset)
    return JobListResponse(jobs=jobs.jobs, total=jobs.total)


@router.post("/jobs", status_code=201)
async def create_job(
    job_data: JobCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Create a new job posting"""
    result = await talent_service.create_job(wallet_address=user_id, job_data=job_data)

    if not result.get("success"):
        raise HTTPException(
            status_code=400, detail=result.get("error", "Failed to create job")
        )

    return result


@router.post("/search", response_model=CandidateListResponse)
async def search_candidates(
    request: CandidateSearchRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Search for validated talent candidates by skills and personality"""
    return await talent_service.search_candidates(
        skills=request.skills,
        personality_types=request.personality_types,
        limit=request.limit,
        offset=request.offset,
    )


@router.get("/candidates", response_model=CandidateListResponse)
async def get_candidates(
    limit: int = 20,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
):
    """Get all validated talent candidates"""
    return await talent_service.get_all_candidates(limit=limit, offset=offset)


@router.post("/offers", status_code=201)
async def create_offer(
    offer_data: OfferCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Create a job offer for a talent"""
    result = await talent_service.create_offer(offer_data)

    if not result.get("success"):
        raise HTTPException(
            status_code=400, detail=result.get("error", "Failed to create offer")
        )

    return result


@router.post("/offers/{offer_id}/accept", response_model=OfferActionResponse)
async def accept_offer(
    offer_id: int,
    user_id: str = Depends(get_current_user_id),
):
    """Accept a job offer (talent only)"""
    return await talent_service.accept_offer(offer_id)


@router.post("/offers/{offer_id}/reject", response_model=OfferActionResponse)
async def reject_offer(
    offer_id: int,
    user_id: str = Depends(get_current_user_id),
):
    """Reject a job offer (talent only)"""
    return await talent_service.reject_offer(offer_id)


@router.get("/offers", response_model=OfferListResponse)
async def get_my_offers(
    user_id: str = Depends(get_current_user_id),
):
    """Get all offers for the current talent user"""
    return await talent_service.get_talent_offers(user_id)


@router.get("/health")
async def health_check():
    """Check if blockchain connection is healthy"""
    is_connected = talent_service.is_connected()
    return {
        "status": "healthy" if is_connected else "degraded",
        "blockchain_connected": is_connected,
    }

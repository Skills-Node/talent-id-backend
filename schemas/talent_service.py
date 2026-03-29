from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str
    industry: str
    website: str


class CompanyResponse(BaseModel):
    id: int
    owner: str
    name: str
    description: str
    industry: str
    website: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str
    requirements: str
    salary_min: int = Field(ge=0)
    salary_max: int = Field(ge=0)
    location: str
    is_remote: bool = False
    required_skills: List[str] = Field(default_factory=list)
    preferred_personality_types: List[str] = Field(default_factory=list)
    employment_type: str = "full-time"


class JobResponse(BaseModel):
    id: int
    company_id: int
    company_owner: str
    title: str
    description: str
    requirements: str
    salary_min: int
    salary_max: int
    location: str
    is_remote: bool
    required_skills: List[str]
    preferred_personality_types: List[str]
    employment_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int


class CandidateSearchRequest(BaseModel):
    skills: Optional[List[str]] = Field(default_factory=list)
    personality_types: Optional[List[str]] = Field(default_factory=list)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class CandidateResponse(BaseModel):
    token_id: int
    wallet_address: str
    profile_uri: str
    personality_type: Optional[str] = None
    competencies: Optional[List[dict]] = None
    skills: Optional[List[str]] = None


class CandidateListResponse(BaseModel):
    candidates: List[CandidateResponse]
    total: int


class OfferCreate(BaseModel):
    job_id: int
    talent_address: str
    token_id: int
    terms: str
    salary: int = Field(ge=0)


class OfferResponse(BaseModel):
    id: int
    job_id: int
    company: str
    talent_address: str
    token_id: int
    terms: str
    salary: int
    status: int
    created_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OfferListResponse(BaseModel):
    offers: List[OfferResponse]
    total: int


class OfferActionResponse(BaseModel):
    success: bool
    message: str
    offer: OfferResponse

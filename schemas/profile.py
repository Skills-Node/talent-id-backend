from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Competency(BaseModel):
    name: str = Field(
        description="Name of the competency (e.g., Leadership, Resilience)"
    )
    value: int = Field(description="Competency value from 0 to 100", ge=0, le=100)


class LeadershipType(BaseModel):
    archetype: str = Field(description="Leadership archetype name")
    description: str = Field(description="Detailed explanation of leadership style")


class ProfileAIOutput(BaseModel):
    personality_type: str
    competencies: List[Competency]
    leadership_style: str
    compatibility: str


class TalentProfile(BaseModel):
    profile_synthesis: str = Field(
        description="Deep 2-3 paragraph text about the candidate's essence"
    )
    leadership_type: LeadershipType
    communication_style: str
    team_role: str
    key_competencies: List[Competency]
    growth_areas: List[str]


class ProfileRequestInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    date_of_birth: str
    enneagram_answers: str = Field(min_length=1)


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    name: str
    date_of_birth: str
    enneagram_answers: str
    profile_synthesis: Optional[str] = None
    leadership_type: Optional[LeadershipType] = None
    communication_style: Optional[str] = None
    team_role: Optional[str] = None
    key_competencies: Optional[List[Competency]] = None
    growth_areas: Optional[List[str]] = None
    personality_type: Optional[str] = None
    competencies: Optional[List[Competency]] = None
    leadership_style: Optional[str] = None
    compatibility: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    profiles: List[ProfileResponse]
    total: int


class ProfileCreateResponse(BaseModel):
    profile: ProfileResponse
    ai_response: Optional[ProfileAIOutput] = None

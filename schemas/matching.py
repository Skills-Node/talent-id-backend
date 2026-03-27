from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MatchingRequestInput(BaseModel):
    profile_id: str
    leader_data: str = Field(
        min_length=1,
        description="What kind of leader or team member the user is looking for",
    )


class MatchingAIOutput(BaseModel):
    match_percentage: int = Field(
        ge=0, le=100, description="Percentage of compatibility"
    )
    strengths: List[str] = Field(
        description="Points where the profiles complement each other"
    )
    conflict_zones: List[str] = Field(description="Potential areas of friction")


class MatchingResponse(BaseModel):
    id: str
    profile_id: str
    leader_personality_type: Optional[str] = None
    leader_data: Optional[str] = None
    match_percentage: Optional[int] = None
    strengths: Optional[List[str]] = None
    conflict_zones: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MatchingListResponse(BaseModel):
    matchings: List[MatchingResponse]
    total: int


class MatchingCreateResponse(BaseModel):
    matching: MatchingResponse
    ai_response: Optional[MatchingAIOutput] = None

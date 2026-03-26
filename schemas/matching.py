from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MatchingRequestInput(BaseModel):
    profile_id: str
    datos_lider: str = Field(min_length=1)


class MatchingResponseOutput(BaseModel):
    porcentaje_match: int = Field(ge=0, le=100)
    puntos_fuertes: List[str]
    zonas_conflicto: List[str]


class MatchingResponse(BaseModel):
    id: str
    profile_id: str
    lider_tipo_personalidad: Optional[str] = None
    lider_datos: Optional[str] = None
    porcentaje_match: Optional[int] = None
    puntos_fuertes: Optional[List[str]] = None
    zonas_conflicto: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MatchingListResponse(BaseModel):
    matchings: List[MatchingResponse]
    total: int


class MatchingCreateResponse(BaseModel):
    matching: MatchingResponse
    ai_response: Optional[MatchingResponseOutput] = None

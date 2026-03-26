from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Competencia(BaseModel):
    nombre: str = Field(
        description="Nombre de la competencia (ej. Liderazgo, Resiliencia)"
    )
    valor: int = Field(description="Valor de la competencia de 0 a 100", ge=0, le=100)


class PerfilRequestInput(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    fecha_nacimiento: str
    respuestas_eneagrama: str = Field(min_length=1)


class PerfilResponseOutput(BaseModel):
    tipo_personalidad: str
    competencias: List[Competencia]
    estilo_liderazgo: str
    compatibilidad: str


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    nombre: str
    fecha_nacimiento: str
    respuestas_eneagrama: str
    tipo_personalidad: Optional[str] = None
    competencias: Optional[List[Competencia]] = None
    estilo_liderazgo: Optional[str] = None
    compatibilidad: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    profiles: List[ProfileResponse]
    total: int


class ProfileCreateResponse(BaseModel):
    profile: ProfileResponse
    ai_response: Optional[PerfilResponseOutput] = None

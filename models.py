from pydantic import BaseModel, Field
from typing import List

class Competencia(BaseModel):
    nombre: str = Field(description="Nombre de la competencia (ej. Liderazgo, Resiliencia)")
    valor: int = Field(description="Valor de la competencia de 0 a 100", ge=0, le=100)

class PerfilResponse(BaseModel):
    tipo_personalidad: str = Field(description="El tipo de personalidad (ej. Eneatipo 3, INTJ, etc.)")
    competencias: List[Competencia] = Field(description="5 competencias clave con un valor de 0 a 100")
    estilo_liderazgo: str = Field(description="Breve descripción de su estilo de liderazgo")
    compatibilidad: str = Field(description="Qué tipo de cultura o líder hace mejor match con este perfil")

class PerfilRequest(BaseModel):
    nombre: str
    fecha_nacimiento: str
    respuestas_eneagrama: str

class MatchingRequest(BaseModel):
    datos_lider: str
    datos_candidato: str

class MatchingResponse(BaseModel):
    porcentaje_match: int = Field(description="Porcentaje de compatibilidad de 0 a 100", ge=0, le=100)
    puntos_fuertes: List[str] = Field(description="Lista de puntos fuertes de la combinación")
    zonas_conflicto: List[str] = Field(description="Lista de zonas de conflicto probable")

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import ProfileRepository
from schemas import (
    PerfilRequestInput,
    PerfilResponseOutput,
    ProfileResponse,
    ProfileListResponse,
    ProfileCreateResponse,
)
from core import NotFoundException, get_logger
from google import genai
from google.genai import types
import json

logger = get_logger()


class ProfileService:
    def __init__(self, db: AsyncSession, gemini_client=None):
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.gemini_client = gemini_client

    async def create_profile(
        self, user_id: str, request: PerfilRequestInput
    ) -> ProfileCreateResponse:
        profile = await self.profile_repo.create(
            user_id=user_id,
            nombre=request.nombre,
            fecha_nacimiento=request.fecha_nacimiento,
            respuestas_eneagrama=request.respuestas_eneagrama,
        )

        ai_response = None
        if self.gemini_client:
            ai_response = await self._generate_profile_with_ai(request)
            if ai_response:
                profile = await self.profile_repo.update(
                    profile_id=profile.id,
                    user_id=user_id,
                    tipo_personalidad=ai_response.tipo_personalidad,
                    competencias=[c.model_dump() for c in ai_response.competencias],
                    estilo_liderazgo=ai_response.estilo_liderazgo,
                    compatibilidad=ai_response.compatibilidad,
                )

        return ProfileCreateResponse(
            profile=ProfileResponse.model_validate(profile),
            ai_response=ai_response,
        )

    async def _generate_profile_with_ai(
        self, request: PerfilRequestInput
    ) -> Optional[PerfilResponseOutput]:
        prompt = f"""
        Actúa como un psicólogo experto en evaluación de talento.
        Analiza al siguiente candidato para generar un Perfil de Talento psicométrico.
        
        Nombre: {request.nombre}
        Fecha de nacimiento: {request.fecha_nacimiento}
        Respuestas del cuestionario (Eneagrama/Psicométrico): {request.respuestas_eneagrama}

        Genera un perfil estructurado con:
        1. tipo_personalidad: El tipo de personalidad (ej. Eneatipo 3, INTJ, etc.)
        2. competencias: Exactamente 5 competencias clave con un valor de 0 a 100.
        3. estilo_liderazgo: Breve descripción de su estilo de liderazgo.
        4. compatibilidad: Qué tipo de cultura o líder hace mejor match con este perfil.
        
        Responde SOLO con JSON válido en este formato exacto:
        {{
            "tipo_personalidad": "string",
            "competencias": [
                {{"nombre": "string", "valor": 0-100}},
                ...
            ],
            "estilo_liderazgo": "string",
            "compatibilidad": "string"
        }}
        """

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                ),
            )
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            return PerfilResponseOutput(**data)
        except Exception as e:
            logger.error(f"Error generating profile with AI: {e}")
            return None

    async def get_profile(self, user_id: str, profile_id: str) -> ProfileResponse:
        profile = await self.profile_repo.get_by_user_and_id(user_id, profile_id)
        if not profile:
            raise NotFoundException("Profile not found")
        return ProfileResponse.model_validate(profile)

    async def list_profiles(self, user_id: str) -> ProfileListResponse:
        profiles = await self.profile_repo.get_by_user_id(user_id)
        total = await self.profile_repo.count_by_user(user_id)
        return ProfileListResponse(
            profiles=[ProfileResponse.model_validate(p) for p in profiles],
            total=total,
        )

    async def delete_profile(self, user_id: str, profile_id: str) -> None:
        await self.profile_repo.delete(profile_id, user_id)

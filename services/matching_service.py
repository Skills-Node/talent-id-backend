from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import MatchingRepository, ProfileRepository
from schemas import (
    MatchingRequestInput,
    MatchingResponseOutput,
    MatchingResponse,
    MatchingListResponse,
    MatchingCreateResponse,
)
from core import NotFoundException, get_logger
from google import genai
from google.genai import types
import json

logger = get_logger()


class MatchingService:
    def __init__(self, db: AsyncSession, gemini_client=None):
        self.db = db
        self.matching_repo = MatchingRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.gemini_client = gemini_client

    async def create_matching(
        self, user_id: str, request: MatchingRequestInput
    ) -> MatchingCreateResponse:
        profile = await self.profile_repo.get_by_user_and_id(
            user_id, request.profile_id
        )
        if not profile:
            raise NotFoundException("Profile not found")

        matching = await self.matching_repo.create(
            profile_id=request.profile_id,
            lider_datos=request.datos_lider,
        )

        ai_response = None
        if self.gemini_client and profile.tipo_personalidad:
            ai_response = await self._generate_matching_with_ai(
                profile=profile,
                lider_datos=request.datos_lider,
            )
            if ai_response:
                matching.lider_tipo_personalidad = (
                    f"Candidate: {profile.tipo_personalidad}"
                )
                matching.porcentaje_match = ai_response.porcentaje_match
                matching.puntos_fuertes = ai_response.puntos_fuertes
                matching.zonas_conflicto = ai_response.zonas_conflicto
                await self.db.commit()
                await self.db.refresh(matching)

        return MatchingCreateResponse(
            matching=MatchingResponse.model_validate(matching),
            ai_response=ai_response,
        )

    async def _generate_matching_with_ai(
        self, profile, lider_datos: str
    ) -> Optional[MatchingResponseOutput]:
        prompt = f"""
        Actúa como un experto en recursos humanos y dinámica de equipos.
        Analiza los siguientes perfiles para determinar su compatibilidad laboral.
        
        Datos del Líder: {lider_datos}
        Datos del Candidato: 
        - Tipo de Personalidad: {profile.tipo_personalidad}
        - Estilo de Liderazgo: {profile.estilo_liderazgo}
        - Compatibilidad: {profile.compatibilidad}

        Genera un Informe de Compatibilidad estructurado con:
        1. porcentaje_match: Un valor de 0 a 100 indicando la compatibilidad general.
        2. puntos_fuertes: Una lista de 3 a 5 puntos fuertes de esta combinación de trabajo.
        3. zonas_conflicto: Una lista de 2 a 3 posibles zonas de fricción o conflicto probable.
        
        Responde SOLO con JSON válido en este formato exacto:
        {{
            "porcentaje_match": 0-100,
            "puntos_fuertes": ["string", ...],
            "zonas_conflicto": ["string", ...]
        }}
        """

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                ),
            )
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            return MatchingResponseOutput(**data)
        except Exception as e:
            logger.error(f"Error generating matching with AI: {e}")
            return None

    async def get_matching(self, matching_id: str) -> MatchingResponse:
        matching = await self.matching_repo.get_by_id(matching_id)
        if not matching:
            raise NotFoundException("Matching not found")
        return MatchingResponse.model_validate(matching)

    async def list_matchings(self, profile_id: str) -> MatchingListResponse:
        matchings = await self.matching_repo.get_by_profile_id(profile_id)
        total = await self.matching_repo.count_by_profile(profile_id)
        return MatchingListResponse(
            matchings=[MatchingResponse.model_validate(m) for m in matchings],
            total=total,
        )

    async def delete_matching(self, matching_id: str) -> None:
        await self.matching_repo.delete(matching_id)

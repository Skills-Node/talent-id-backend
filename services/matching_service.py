from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import MatchingRepository, ProfileRepository
from schemas import (
    MatchingRequestInput,
    MatchingAIOutput,
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
            leader_data=request.leader_data,
        )

        ai_response = None
        if self.gemini_client and profile.personality_type:
            ai_response = await self._generate_matching_with_ai(
                profile=profile,
                leader_data=request.leader_data,
            )
            if ai_response:
                matching.leader_personality_type = (
                    f"Candidate: {profile.personality_type}"
                )
                matching.match_percentage = ai_response.match_percentage
                matching.strengths = ai_response.strengths
                matching.conflict_zones = ai_response.conflict_zones
                await self.db.commit()
                await self.db.refresh(matching)

        return MatchingCreateResponse(
            matching=MatchingResponse.model_validate(matching),
            ai_response=ai_response,
        )

    async def _generate_matching_with_ai(
        self, profile, leader_data: str
    ) -> Optional[MatchingAIOutput]:
        prompt = f"""
You are an expert in HR and team dynamics. Analyze the following profiles to determine their workplace compatibility.

Leader/Candidate Profile Data:
- Leader Preferences: {leader_data}
- Candidate Personality Type: {profile.personality_type}
- Candidate Leadership Style: {profile.leadership_style}
- Candidate Compatibility: {profile.compatibility}

Generate a Compatibility Report with:
1. match_percentage: A value from 0 to 100 indicating overall compatibility.
2. strengths: A list of 3-5 key strengths of this working combination.
3. conflict_zones: A list of 2-3 potential friction areas or likely conflicts.

Respond ONLY with valid JSON in this exact format:
{{
  "match_percentage": 0-100,
  "strengths": ["string", ...],
  "conflict_zones": ["string", ...]
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
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            return MatchingAIOutput(**data)
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

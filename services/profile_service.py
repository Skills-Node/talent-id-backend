from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import ProfileRepository
from schemas import (
    ProfileRequestInput,
    ProfileAIOutput,
    ProfileResponse,
    ProfileListResponse,
    ProfileCreateResponse,
    TalentProfile,
    Competency,
)
from core import NotFoundException, get_logger
import json

logger = get_logger()


class ProfileService:
    def __init__(self, db: AsyncSession, ollama_client=None):
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.ollama_client = ollama_client

    async def create_profile(
        self, user_id: str, request: ProfileRequestInput
    ) -> ProfileCreateResponse:
        profile = await self.profile_repo.create(
            user_id=user_id,
            name=request.name,
            date_of_birth=request.date_of_birth,
            enneagram_answers=request.enneagram_answers,
        )

        ai_response = None
        if self.ollama_client:
            ai_response = await self._generate_profile_with_ai(request)
            if ai_response:
                competency_list = [
                    {"name": c.name, "value": c.value}
                    for c in ai_response.key_competencies
                ]
                profile = await self.profile_repo.update(
                    profile_id=profile.id,
                    user_id=user_id,
                    personality_type=ai_response.leadership_type.archetype,
                    competencies=competency_list,
                    leadership_style=ai_response.communication_style,
                    compatibility=ai_response.team_role,
                    profile_synthesis=ai_response.profile_synthesis,
                    leadership_type={
                        "archetype": ai_response.leadership_type.archetype,
                        "description": ai_response.leadership_type.description,
                    },
                    communication_style=ai_response.communication_style,
                    team_role=ai_response.team_role,
                    key_competencies=competency_list,
                    growth_areas=ai_response.growth_areas,
                )

        return ProfileCreateResponse(
            profile=ProfileResponse.model_validate(profile),
            ai_response=None,
        )

    async def _generate_profile_with_ai(
        self, request: ProfileRequestInput
    ) -> Optional[TalentProfile]:
        prompt = f"""
You are an expert in organizational psychology, ontological coaching, and high-performance team dynamics. Your goal is to analyze a professional's data and generate a deep, accurate "Comprehensive Talent Profile" without empty corporate jargon. IMPORTANT: All content must be in ENGLISH only.

Candidate Input Data:
- Name: {request.name}
- Date of birth: {request.date_of_birth}
- Enneagram questionnaire answers: {request.enneagram_answers}

Profile Synthesis: Get to the core essence of the person. Do not simply describe their technical experience, but rather how they processes information, what motivates them, and how they operate internally.

Leadership Type: Define their leadership archetype. Explain how they influence others, where they lead from, and how they make decisions.

Communication Style: Identify their most distinctive communication traits and explain how they impact the rest of the team.

Team Role: Define the natural roles they assume when working with others.

Key Competencies: Extract exactly 5 fundamental skills and assign them a mastery percentage from 0 to 100.

Growth Areas / Conflict Zones: Identify blind spots or probable frictions. Formulate them as areas of attention.

Mandatory Output Format (Strict JSON - English only):
{{
  "profile_synthesis": "Deep 2-3 paragraph text about the candidate's essence in English...",
  "leadership_type": {{
    "archetype": "Name of the archetype (e.g., Transformational Leadership)",
    "description": "Detailed explanation of the leadership style..."
  }},
  "communication_style": "Description of communication style...",
  "team_role": "Natural role in teams (e.g., The Solutions Architect)",
  "key_competencies": [
    {{"name": "Skill Name", "value": 0-100}},
    {{"name": "Skill Name", "value": 0-100}},
    {{"name": "Skill Name", "value": 0-100}},
    {{"name": "Skill Name", "value": 0-100}},
    {{"name": "Skill Name", "value": 0-100}}
  ],
  "growth_areas": ["Area 1", "Area 2", "Area 3"]
}}

Respond ONLY with valid JSON in English, no additional text.
"""

        try:
            response = self.ollama_client.chat(
                model="mistral",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={"temperature": 0.2},
            )
            text = response["message"]["content"].strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            return TalentProfile(**data)
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

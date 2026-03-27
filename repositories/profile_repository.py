from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import Profile
from core import NotFoundException


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, profile_id: str) -> Optional[Profile]:
        result = await self.db.execute(select(Profile).where(Profile.id == profile_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> List[Profile]:
        result = await self.db.execute(
            select(Profile)
            .where(Profile.user_id == user_id)
            .order_by(Profile.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user_and_id(
        self, user_id: str, profile_id: str
    ) -> Optional[Profile]:
        result = await self.db.execute(
            select(Profile).where(
                Profile.id == profile_id,
                Profile.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: str,
        name: str,
        date_of_birth: str,
        enneagram_answers: str,
    ) -> Profile:
        profile = Profile(
            user_id=user_id,
            name=name,
            date_of_birth=date_of_birth,
            enneagram_answers=enneagram_answers,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update(
        self,
        profile_id: str,
        user_id: str,
        personality_type: str = None,
        competencies: dict = None,
        leadership_style: str = None,
        compatibility: str = None,
        profile_synthesis: str = None,
        leadership_type: dict = None,
        communication_style: str = None,
        team_role: str = None,
        key_competencies: dict = None,
        growth_areas: dict = None,
    ) -> Profile:
        profile = await self.get_by_user_and_id(user_id, profile_id)
        if not profile:
            raise NotFoundException("Profile not found")

        if personality_type is not None:
            profile.personality_type = personality_type
        if competencies is not None:
            profile.competencies = competencies
        if leadership_style is not None:
            profile.leadership_style = leadership_style
        if compatibility is not None:
            profile.compatibility = compatibility
        if profile_synthesis is not None:
            profile.profile_synthesis = profile_synthesis
        if leadership_type is not None:
            profile.leadership_type = leadership_type
        if communication_style is not None:
            profile.communication_style = communication_style
        if team_role is not None:
            profile.team_role = team_role
        if key_competencies is not None:
            profile.key_competencies = key_competencies
        if growth_areas is not None:
            profile.growth_areas = growth_areas

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def delete(self, profile_id: str, user_id: str) -> None:
        profile = await self.get_by_user_and_id(user_id, profile_id)
        if not profile:
            raise NotFoundException("Profile not found")
        await self.db.delete(profile)
        await self.db.commit()

    async def count_by_user(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.count(Profile.id)).where(Profile.user_id == user_id)
        )
        return result.scalar() or 0

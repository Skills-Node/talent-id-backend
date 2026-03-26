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
        nombre: str,
        fecha_nacimiento: str,
        respuestas_eneagrama: str,
    ) -> Profile:
        profile = Profile(
            user_id=user_id,
            nombre=nombre,
            fecha_nacimiento=fecha_nacimiento,
            respuestas_eneagrama=respuestas_eneagrama,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update(
        self,
        profile_id: str,
        user_id: str,
        tipo_personalidad: str = None,
        competencias: dict = None,
        estilo_liderazgo: str = None,
        compatibilidad: str = None,
    ) -> Profile:
        profile = await self.get_by_user_and_id(user_id, profile_id)
        if not profile:
            raise NotFoundException("Profile not found")

        if tipo_personalidad is not None:
            profile.tipo_personalidad = tipo_personalidad
        if competencias is not None:
            profile.competencias = competencias
        if estilo_liderazgo is not None:
            profile.estilo_liderazgo = estilo_liderazgo
        if compatibilidad is not None:
            profile.compatibilidad = compatibilidad

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

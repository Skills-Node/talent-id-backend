from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import Matching
from core import NotFoundException


class MatchingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, matching_id: str) -> Optional[Matching]:
        result = await self.db.execute(
            select(Matching).where(Matching.id == matching_id)
        )
        return result.scalar_one_or_none()

    async def get_by_profile_id(self, profile_id: str) -> List[Matching]:
        result = await self.db.execute(
            select(Matching)
            .where(Matching.profile_id == profile_id)
            .order_by(Matching.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        profile_id: str,
        lider_tipo_personalidad: str = None,
        lider_datos: str = None,
        porcentaje_match: int = None,
        puntos_fuertes: list = None,
        zonas_conflicto: list = None,
    ) -> Matching:
        matching = Matching(
            profile_id=profile_id,
            lider_tipo_personalidad=lider_tipo_personalidad,
            lider_datos=lider_datos,
            porcentaje_match=porcentaje_match,
            puntos_fuertes=puntos_fuertes,
            zonas_conflicto=zonas_conflicto,
        )
        self.db.add(matching)
        await self.db.commit()
        await self.db.refresh(matching)
        return matching

    async def delete(self, matching_id: str) -> None:
        matching = await self.get_by_id(matching_id)
        if not matching:
            raise NotFoundException("Matching not found")
        await self.db.delete(matching)
        await self.db.commit()

    async def count_by_profile(self, profile_id: str) -> int:
        result = await self.db.execute(
            select(func.count(Matching.id)).where(Matching.profile_id == profile_id)
        )
        return result.scalar() or 0

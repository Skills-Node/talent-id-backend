from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base
import uuid


class Matching(Base):
    __tablename__ = "matchings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(
        String(36),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lider_tipo_personalidad = Column(String(100), nullable=True)
    lider_datos = Column(Text, nullable=True)

    porcentaje_match = Column(Integer, nullable=True)
    puntos_fuertes = Column(JSON, nullable=True)
    zonas_conflicto = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="matchings")

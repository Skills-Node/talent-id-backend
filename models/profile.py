from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base
import uuid


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nombre = Column(String(255), nullable=False)
    fecha_nacimiento = Column(String(50), nullable=False)
    respuestas_eneagrama = Column(Text, nullable=False)

    tipo_personalidad = Column(String(100), nullable=True)
    competencias = Column(JSON, nullable=True)
    estilo_liderazgo = Column(Text, nullable=True)
    compatibilidad = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="profiles")
    matchings = relationship(
        "Matching", back_populates="profile", cascade="all, delete-orphan"
    )

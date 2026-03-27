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

    name = Column(String(255), nullable=False)
    date_of_birth = Column(String(50), nullable=False)
    enneagram_answers = Column(Text, nullable=False)

    personality_type = Column(String(100), nullable=True)
    profile_synthesis = Column(Text, nullable=True)
    leadership_type = Column(JSON, nullable=True)
    communication_style = Column(Text, nullable=True)
    team_role = Column(Text, nullable=True)
    key_competencies = Column(JSON, nullable=True)
    growth_areas = Column(JSON, nullable=True)
    competencies = Column(JSON, nullable=True)
    leadership_style = Column(Text, nullable=True)
    compatibility = Column(Text, nullable=True)

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

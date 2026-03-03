import uuid
import enum
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.db.base import Base


class InterviewConfig(Base):
    __tablename__ = "interview_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    # Interview content
    opening_script = Column(Text, nullable=False)
    interview_prompt = Column(Text, nullable=False)
    marking_prompt = Column(Text, nullable=False)

    # Limits
    max_questions = Column(Integer, default=5)
    max_duration_minutes = Column(Integer, default=15)

    # Call Window (NEW)
    call_start_time = Column(Time, nullable=False)   # e.g. 09:00
    call_end_time = Column(Time, nullable=False)     # e.g. 18:00
    timezone = Column(String, default="Asia/Kolkata")

    # Versioning & status
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
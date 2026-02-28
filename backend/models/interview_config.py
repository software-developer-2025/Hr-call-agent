import uuid
from sqlalchemy import Column, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base


class InterviewConfig(Base):
    __tablename__ = "interview_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    opening_script = Column(Text)
    interview_prompt = Column(Text)
    marking_prompt = Column(Text)
    max_questions = Column(Integer)
    max_duration_minutes = Column(Integer)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
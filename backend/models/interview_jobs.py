import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base
from backend.models.candidate import InterviewStatus


class InterviewJob(Base):
    __tablename__ = "interview_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    scheduled_time = Column(DateTime)
    priority = Column(Integer, default=1)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.queued)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
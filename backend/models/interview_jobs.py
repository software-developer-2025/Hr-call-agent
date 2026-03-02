import uuid
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.db.base import Base


class InterviewJob(Base):
    __tablename__ = "interview_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False
    )

    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="queued")
    # queued | calling | completed | failed
    priority = Column(Integer, default=1)
    retry_count = Column(Integer, default=0)
    last_error = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (
        Index("idx_jobs_status", "status"),
    )
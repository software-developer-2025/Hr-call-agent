import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    batch_id = Column(UUID(as_uuid=True), ForeignKey("candidate_batches.id", ondelete="SET NULL"))

    name = Column(String)
    phone = Column(String)
    email = Column(String)
    resume_text = Column(String)
    experience_years = Column(Integer)
    status = Column(String, default="queued")

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_candidates_batch_id", "batch_id"),
        Index("idx_candidates_status", "status"),
    )
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.db.base import Base
import enum


class InterviewStatus(str, enum.Enum):
    queued = "queued"
    scheduled = "scheduled"
    calling = "calling"
    in_progress = "in_progress"
    evaluating = "evaluating"
    completed = "completed"
    failed = "failed"
    rescheduled = "rescheduled"
    not_received = "not_received"


class CandidateBatch(Base):
    __tablename__ = "candidate_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    filename = Column(String)
    total_records = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    batch_id = Column(UUID(as_uuid=True), ForeignKey("candidate_batches.id", ondelete="SET NULL"))
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    resume_text = Column(Text)
    experience_years = Column(Integer)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.queued)
    created_at = Column(DateTime, server_default=func.now())
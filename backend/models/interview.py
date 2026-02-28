import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Float, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from backend.db.base import Base
import enum


class CallStatus(str, enum.Enum):
    ringing = "ringing"
    answered = "answered"
    no_answer = "no_answer"
    busy = "busy"
    failed = "failed"
    completed = "completed"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    call_status = Column(Enum(CallStatus))
    total_questions = Column(Integer)
    total_answers = Column(Integer)
    overall_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
import uuid
from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base import Base
from backend.models.interview import CallStatus  # enum


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id"),
        nullable=False
    )

    twilio_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("twilio_accounts.id")
    )

    interview_config_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interview_configs.id")
    )

    llm_config_id = Column(
        UUID(as_uuid=True),
        ForeignKey("llm_configs.id")
    )

    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)

    call_status = Column(Enum(CallStatus))

    total_questions = Column(Integer)
    total_answers = Column(Integer)

    overall_score = Column(Float)

    created_at = Column(DateTime, server_default=func.now())

    # Optional ORM relationships (recommended)
    company = relationship("Company")
    candidate = relationship("Candidate")
    twilio_account = relationship("TwilioAccount")
    interview_config = relationship("InterviewConfig")
    llm_config = relationship("LLMConfig")
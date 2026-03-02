import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.db.base import Base


class CandidateBatch(Base):
    __tablename__ = "candidate_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    filename = Column(String, nullable=False)
    total_records = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
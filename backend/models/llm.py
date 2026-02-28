
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from backend.db.base import Base


class LLMConfig(Base):
    __tablename__ = "llm_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    provider = Column(String)
    model_name = Column(String)
    encrypted_api_key = Column(String)
    max_tokens = Column(Integer)
    temperature = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
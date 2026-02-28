import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from backend.db.base import Base


class TwilioAccount(Base):
    __tablename__ = "twilio_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    account_sid = Column(String)
    encrypted_auth_token = Column(String)
    outbound_number = Column(String)
    region = Column(String)
    cps_limit = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
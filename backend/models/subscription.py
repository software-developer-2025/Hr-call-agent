import uuid
from sqlalchemy import Column, String, Date, Enum, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.db.base import Base
import enum


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    max_calls_per_day = Column(Integer)
    max_concurrent_calls = Column(Integer)
    max_tokens_per_month = Column(Integer)
    price = Column(Float)


class CompanySubscription(Base):
    __tablename__ = "company_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum(SubscriptionStatus))
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, index=True)
    action = Column(String, nullable=False) # e.g. "USER_LOGIN", "SUBSCRIPTION_CREATED"
    details = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

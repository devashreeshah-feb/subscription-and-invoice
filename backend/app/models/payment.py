import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    
    amount = Column(Integer, nullable=False) # In cents
    currency = Column(String, default="INR")
    status = Column(String, default="pending") # pending, success, failed
    gateway = Column(String, default="stripe_test")
    transaction_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    subscription = relationship("Subscription", backref="payments")
